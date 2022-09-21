
from skimage.io import imread
import os, os.path
import numpy as np
import pandas as pd
import torchxrayvision as xrv
import torchvision, torchvision.transforms

import json
from torchxrayvision.datasets import normalize, Dataset


class XNAT_Dataset(Dataset):

    def __init__(self, index,
                 seed):

        super(XNAT_Dataset, self).__init__()
        np.random.seed(seed)  # Reset the seed so all runs are the same.
        self.index = index
        self.keys = list(index.keys())
        self.transforms = torchvision.transforms.Compose([xrv.datasets.XRayCenterCrop(),xrv.datasets.XRayResizer(224)])
        self.classes = ['Lesion', 'Pleural_Abnormalities', 'No_Finding', 'Consolidation', 'Cardiomegaly', 'Pneumonia', 'Pleural_Effusion', 'Opacity', 'Atelectasis']

    def __len__(self):
        return len(self.index)

    def _one_hot(self, labels):
        output = []
        for class_ in self.classes:
            curr = 1.0 if class_ in labels else 0.0
            output.append(curr)
        output = np.array(output, np.float64)
        return output

    def __getitem__(self, idx):
        samples = {}
        try:
            key = self.keys[idx]
            image_file, label_file = self.index[key]['dicom'], self.index[key]['label']
            
            img_path = image_file

            img = imread(img_path)

            img = normalize(img, maxval=65535, reshape=True)
            img = self.transforms(img)
            labels = json.load(open(label_file))[0]
            samples['img'] = img
            samples['lab'] = self._one_hot(labels)
        except Exception as e:
            print(f'Failed to load {idx}, {image_file}', e)
        return samples
