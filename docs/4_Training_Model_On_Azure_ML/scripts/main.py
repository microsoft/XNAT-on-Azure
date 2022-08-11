import os,sys
import os,sys,inspect
import numpy as np
import argparse
import torch
import torchvision, torchvision.transforms
import sklearn, sklearn.model_selection
import training_util
import random
import torchxrayvision as xrv
import multiprocessing

from glob import glob
from os.path import exists, join
from tqdm import tqdm
from xnat_dataset import XNAT_Dataset
from azureml.core import Dataset
from azureml.core import Run
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


def build_index(dataset_dir: str) -> dict:
    index = {}


    bad_images = [
        '2.25.240946342794774843770786948820358276036-no-value-for-SeriesNumber-no-value-for-InstanceNumber-1hxt338.dcm',
        '2.25.162544883334287253626487052063817457451-no-value-for-SeriesNumber-no-value-for-InstanceNumber-d80mgd.dcm'
        '2.25.136638010606859898494927392621300143308-no-value-for-SeriesNumber-no-value-for-InstanceNumber-83hx6r.dcm',
        '2.25.184647331426591649253929737534130703076-no-value-for-SeriesNumber-no-value-for-InstanceNumber-1i9ypb6.dcm',
        '2.25.237832309509942405217773563817142936483-no-value-for-SeriesNumber-no-value-for-InstanceNumber-1gwpzab.dcm',
        '2.25.187267419463228299673575698052257300792-no-value-for-SeriesNumber-no-value-for-InstanceNumber-1ns51cg.dcm',
        '2.25.260914798500543416152343862021057055464-no-value-for-SeriesNumber-no-value-for-InstanceNumber-53q2qb.dcm',
        '2.25.127311252165827658097134604078285869277-no-value-for-SeriesNumber-no-value-for-InstanceNumber-ih8zpj.dcm',
        '2.25.127461990201124141508039840633000411643-no-value-for-SeriesNumber-no-value-for-InstanceNumber-1tezgzi.dcm',
        '2.25.141662369087515829760687220246264616151-no-value-for-SeriesNumber-no-value-for-InstanceNumber-1aae1ux.dcm',
        '2.25.16662968263890371781191180186994512147-no-value-for-SeriesNumber-no-value-for-InstanceNumber-y9b6mt.dcm',
        '2.25.114899592762862200625636748648129535352-no-value-for-SeriesNumber-no-value-for-InstanceNumber-1rrrcnp.dcm',
        '2.25.188728196861761936645308110079401146788-no-value-for-SeriesNumber-no-value-for-InstanceNumber-1jzjbhq.dcm',
        '2.25.162544883334287253626487052063817457451-no-value-for-SeriesNumber-no-value-for-InstanceNumber-d80mgd.dcm',
        '2.25.136638010606859898494927392621300143308-no-value-for-SeriesNumber-no-value-for-InstanceNumber-83hx6r.dcm',
        '2.25.103189714674277876202546910611718183498-no-value-for-SeriesNumber-no-value-for-InstanceNumber-clrt68.dcm',
        '2.25.247445426298520307292317404934771952701-no-value-for-SeriesNumber-no-value-for-InstanceNumber-10ba3ez.dcm',
        '2.25.23104667226368533930074141020644988908-no-value-for-SeriesNumber-no-value-for-InstanceNumber-c43wx5.dcm',
        '2.25.258935262966368948120603976556320260526-no-value-for-SeriesNumber-no-value-for-InstanceNumber-udn5k6.dcm',
        
    ]

    for (dirpath, _, files) in os.walk(dataset_dir):
        for f in files:
            abspath = os.path.abspath(os.path.join(dirpath, f))
            # skip if not a DICOM file or annotation
            if not f.endswith('.dcm') and not f.endswith('.json'): continue
            if f in bad_images: continue
            
            # Extract 3rd from the last 
            # Example: /arc001/f2011dd6-5440-0e5e-f160-5a412228871a/SCANS/2_25_159456128528764240534076543365480931671/LABEL/label.json -> 2_25_159456128528764240534076543365480931671
            series_id = abspath.split('/')[-3]
            
            if series_id not in index: index[series_id] = {}
            if f.endswith('.dcm'): index[series_id]['dicom'] = abspath
            else: index[series_id]['label'] = abspath
    out_index = {}
    for key in index.keys():

        if index[key] == {} or 'dicom' not in index[key] or 'label' not in index[key]: continue
        out_index[key] = index[key]
    return out_index

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', type=str, default="", help='')
    parser.add_argument('-name', type=str, default='densenet')
    parser.add_argument('--output_dir', type=str, default="outputs")
    parser.add_argument('--dataset', type=str, default="pc")
    parser.add_argument('--dataset_dir', type=str, default="./data")
    parser.add_argument('--model', type=str, default="densenet")
    parser.add_argument('--seed', type=int, default=0, help='')
    parser.add_argument('--cuda', type=bool, default=True, help='')
    parser.add_argument('--num_epochs', type=int, default=20, help='')
    parser.add_argument('--batch_size_per_gpu', type=int, default=24, help='')
    parser.add_argument('--shuffle', type=bool, default=True, help='')
    parser.add_argument('--lr', type=float, default=0.001, help='')
    parser.add_argument('--threads', type=int, default=multiprocessing.cpu_count(), help='')
    parser.add_argument('--taskweights', type=bool, default=False, help='')
    parser.add_argument('--featurereg', type=bool, default=False, help='')
    parser.add_argument('--weightreg', type=bool, default=False, help='')
    parser.add_argument('--data_aug', type=bool, default=True, help='')
    parser.add_argument('--data_aug_rot', type=int, default=45, help='')
    parser.add_argument('--data_aug_trans', type=float, default=0.15, help='')
    parser.add_argument('--data_aug_scale', type=float, default=0.15, help='')
    parser.add_argument('--label_concat', type=bool, default=False, help='')
    parser.add_argument('--label_concat_reg', type=bool, default=False, help='')
    parser.add_argument('--multicuda', type=bool, default=True, help='')
    parser.add_argument('--azure_ml', type=bool, default=False, help='')
    parser.add_argument('--testing', type=bool, default=False, help='')

    cfg = parser.parse_args()
    cfg.limit = None
    print(f'dataset_dir {cfg.dataset_dir}')
    print('building index....')
    index = build_index(cfg.dataset_dir)
    labels = set()
    import json
    for key in index:
        label = json.load(open(index[key]['label']))[0]
        labels.add(label)
    print(labels)
    dataset = XNAT_Dataset(index, 0)

    model = xrv.models.DenseNet(num_classes=len(dataset.classes), in_channels=1,
                                    **xrv.models.get_densenet_params(cfg.model))
    training_util.train(model, dataset, cfg)

    