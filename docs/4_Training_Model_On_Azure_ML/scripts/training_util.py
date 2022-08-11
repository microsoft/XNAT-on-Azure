import os, copy
import pickle
import pprint
import random
from glob import glob
from os.path import exists, join
from torch.utils.data import random_split

import numpy as np
import torch
import sklearn.metrics
from sklearn.metrics import roc_auc_score, accuracy_score
import sklearn, sklearn.model_selection
import torchxrayvision as xrv


def train(model, dataset, cfg):
    print("Our config:")
    pprint.pprint(cfg)

    #Creates run object to display metrics (e.g., accuracy, etc.)
    if cfg.azure_ml:
        from azureml.core import Run        
        run = Run.get_context()    

    dataset_name = cfg.dataset + "-" + cfg.model + "-" + cfg.name
    
    device = 'cuda' if cfg.cuda else 'cpu'
    if not torch.cuda.is_available() and cfg.cuda:
        device = 'cpu'
        print("WARNING: cuda was requested but is not available, using cpu instead.")

    print(f'Using device: {device}')

    print(cfg.output_dir)

    if not exists(cfg.output_dir):
        os.makedirs(cfg.output_dir)
    
    # Setting the seed
    np.random.seed(cfg.seed)
    random.seed(cfg.seed)
    torch.manual_seed(cfg.seed)

    if cfg.cuda:
        torch.cuda.manual_seed_all(cfg.seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    # Dataset    
    n_train = int(len(dataset)*0.9)
    n_val = len(dataset) - n_train
    train_dataset, valid_dataset = random_split(dataset, [n_train, n_val])
    
    # Dataloader
    train_loader = torch.utils.data.DataLoader(train_dataset,
                                               batch_size=cfg.batch_size_per_gpu,
                                               shuffle=cfg.shuffle,
                                               num_workers=cfg.threads, 
                                               pin_memory=cfg.cuda)
    valid_loader = torch.utils.data.DataLoader(valid_dataset,
                                               batch_size=cfg.batch_size_per_gpu,
                                               shuffle=cfg.shuffle,
                                               num_workers=cfg.threads, 
                                               pin_memory=cfg.cuda)
    # Optimizer
    optim = torch.optim.Adam(model.parameters(), lr=cfg.lr, weight_decay=1e-5, amsgrad=True)
    criterion = torch.nn.BCEWithLogitsLoss()

    if torch.cuda.device_count() > 1:
        print("Will try to use", torch.cuda.device_count(), "GPUs!")
        model = torch.nn.DataParallel(model)


    # Checkpointing
    start_epoch = 0
    best_metric = 0.
    weights_for_best_validauc = None
    auc_test = None
    metrics = []
    weights_files = glob(join(cfg.output_dir, f'{dataset_name}-e*.pt'))  # Find all weights files
    if len(weights_files):
        # Find most recent epoch
        epochs = np.array(
            [int(w[len(join(cfg.output_dir, f'{dataset_name}-e')):-len('.pt')].split('-')[0]) for w in weights_files])
        start_epoch = epochs.max()
        weights_file = [weights_files[i] for i in np.argwhere(epochs == np.amax(epochs)).flatten()][0]
        model.load_state_dict(torch.load(weights_file).state_dict())

        with open(join(cfg.output_dir, f'{dataset_name}-metrics.pkl'), 'rb') as f:
            metrics = pickle.load(f)

        best_metric = metrics[-1]['best_metric']
        weights_for_best_validauc = model.state_dict()

        print("Resuming training at epoch {0}.".format(start_epoch))
        print("Weights loaded: {0}".format(weights_file))

    model.to(device)
    
    for epoch in range(start_epoch, cfg.num_epochs):

        avg_loss = train_epoch(cfg=cfg,
                               epoch=epoch,
                               model=model,
                               device=device,
                               optimizer=optim,
                               train_loader=train_loader,
                               criterion=criterion,
                               limit=cfg.limit)
        print(f'Epoch {epoch + 1} - Train - Loss = {avg_loss:4.4f}')

        auc_valid = valid_test_epoch(name='Valid',
                                     epoch=epoch,
                                     model=model,
                                     device=device,
                                     data_loader=valid_loader,
                                     criterion=criterion,
                                     limit=cfg.limit)[0]
        print(f'Epoch {epoch + 1} - Train - Loss = {avg_loss:4.4f}')


        if np.mean(auc_valid) > best_metric:
            best_metric = np.mean(auc_valid)
            weights_for_best_validauc = model.state_dict()

            model_to_save = copy.deepcopy(model)
            if torch.cuda.device_count() > 1:
                # Saves best model and removes nn.parallel
                model_to_save = model_to_save.module.to(torch.device('cpu'))
            else:
                model_to_save = model_to_save.to(torch.device('cpu'))

            torch.save(model_to_save, join(cfg.output_dir, f'{dataset_name}-best.pt'))

        stat = {
            "epoch": epoch + 1,
            "trainloss": avg_loss,
            "validauc": auc_valid,
            'best_metric': best_metric
        }

        if cfg.azure_ml:
                # Logs training loss and validation accuracy
                run.log("Training Loss", np.float(avg_loss))
                # Area Under the Receiver Operating Characteristic Curve (ROC AUC)
                run.log("ROC AUC", np.float(auc_valid))

        metrics.append(stat)

        with open(join(cfg.output_dir, f'{dataset_name}-metrics.pkl'), 'wb') as f:
            pickle.dump(metrics, f)

    return metrics, best_metric, weights_for_best_validauc


def train_epoch(cfg, epoch, model, device, train_loader, optimizer, criterion, limit=None):
    model.train()

    if cfg.taskweights:
        weights = np.nansum(train_loader.dataset.labels, axis=0)
        weights = weights.max() - weights + weights.mean()
        weights = weights/weights.max()
        weights = torch.from_numpy(weights).to(device).float()
        print("task weights", weights)
    
    avg_loss = []

    for batch_idx, samples in enumerate(train_loader):
        
        if limit and (batch_idx > limit):
            print("breaking out")
            break
            
        optimizer.zero_grad()
        
        images = samples["img"].float().to(device)
        targets = samples["lab"].to(device)

        outputs = model(images)
        
        loss = torch.zeros(1).to(device).float()
        for task in range(targets.shape[1]):
            task_output = outputs[:,task]
            task_target = targets[:,task]
            mask = ~torch.isnan(task_target)
            task_output = task_output[mask]
            task_target = task_target[mask]
            if len(task_target) > 0:
                task_loss = criterion(task_output.float(), task_target.float())
                if cfg.taskweights:
                    loss += weights[task]*task_loss
                else:
                    loss += task_loss
        
        # here regularize the weight matrix when label_concat is used
        if cfg.label_concat_reg:
            if not cfg.label_concat:
                raise Exception("cfg.label_concat must be true")
            weight = model.classifier.weight
            num_labels = len(xrv.datasets.default_pathologies)
            num_datasets = weight.shape[0]//num_labels
            weight_stacked = weight.reshape(num_datasets,num_labels,-1)
            label_concat_reg_lambda = torch.tensor(0.1).to(device).float()
            for task in range(num_labels):
                dists = torch.pdist(weight_stacked[:,task], p=2).mean()
                loss += label_concat_reg_lambda*dists
                
        loss = loss.sum()
        
        if cfg.featurereg:
            feat = model.features(images)
            loss += feat.abs().sum()
            
        if cfg.weightreg:
            loss += model.classifier.weight.abs().sum()
        
        loss.backward()
        avg_loss.append(loss.detach().cpu().numpy())
        optimizer.step()

    print(f'Epoch {epoch + 1} - Train - Loss = {np.mean(avg_loss):4.4f}')        

    return np.mean(avg_loss)

def valid_test_epoch(name, epoch, model, device, data_loader, criterion, limit=None):
    model.eval()

    avg_loss = []
    task_outputs={}
    task_targets={}
    for task in range(data_loader.dataset[0]["lab"].shape[0]):
        task_outputs[task] = []
        task_targets[task] = []
        
    with torch.no_grad():
        for batch_idx, samples in enumerate(data_loader):

            if limit and (batch_idx > limit):
                print("breaking out")
                break
            
            images = samples["img"].to(device)
            targets = samples["lab"].to(device)

            outputs = model(images)
            
            loss = torch.zeros(1).to(device).double()
            for task in range(targets.shape[1]):
                task_output = outputs[:,task]
                task_target = targets[:,task]
                mask = ~torch.isnan(task_target)
                task_output = task_output[mask]
                task_target = task_target[mask]
                if len(task_target) > 0:
                    loss += criterion(task_output.double(), task_target.double())
                
                task_outputs[task].append(task_output.detach().cpu().numpy())
                task_targets[task].append(task_target.detach().cpu().numpy())

            loss = loss.sum()
            
            avg_loss.append(loss.detach().cpu().numpy())
        print(f'Epoch {epoch + 1} - {name} - Loss = {np.mean(avg_loss):4.4f}')
            
        for task in range(len(task_targets)):
            task_outputs[task] = np.concatenate(task_outputs[task])
            task_targets[task] = np.concatenate(task_targets[task])
    
        task_aucs = []
        for task in range(len(task_targets)):
            if len(np.unique(task_targets[task]))> 1:
                task_auc = sklearn.metrics.roc_auc_score(task_targets[task], task_outputs[task])
                task_aucs.append(task_auc)
            else:
                task_aucs.append(np.nan)

    task_aucs = np.asarray(task_aucs)
    auc = np.mean(task_aucs[~np.isnan(task_aucs)])
    print(f'Epoch {epoch + 1} - {name} - Avg AUC = {auc:4.4f}')

    return auc, task_aucs, task_outputs, task_targets