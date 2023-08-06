from os import listdir, makedirs, getcwd, remove
from os.path import isfile, join, abspath, exists, isdir, expanduser
from PIL import Image
import pickle
import nltk
import cv2 , os, time
import numpy as np

import torch
from torch.optim import lr_scheduler
from torch.autograd import Variable
from torch.utils.data import Dataset, DataLoader
import torch.utils.data as data
import torch.nn as nn
import torch.autograd as autograd
from torch.nn import ReLU

import torchvision
from torchvision import transforms, datasets, models

import scipy.misc
import matplotlib.pyplot as plt
import json

class cnn_layer_visualization_by_heatmaps():

    def __init__(self,model,imagenet_class_index_file_path="",output_path=""):
        self.model = model
        self.output_path = output_path
        self.modulelist = list(self.model.features.modules())
        self.labels = json.load(open(imagenet_class_index_file_path))

    def grayscale(self,image):
        image = torch.sum(image, dim=0)
        image = torch.div(image, image.shape[0])
        return image

    def normalize(self,image):
        normalize = transforms.Normalize(
            mean=[0.485,0.456,0.406],
            std=[0.229,0.224,0.225]
        )
        preprocess = transforms.Compose([
            transforms.Resize((224,224)),
            transforms.ToTensor(),
            normalize
        ])

        image = Variable(preprocess(image).unsqueeze(0))

        return image

    def predict(self,image):
        _, index = self.model(image).data[0].max(0)
        return str(index[0]), self.labels[str(index)][1]

    def deprocess(self,image):
        return image * torch.Tensor([0.229,0.224,0.225]) + torch.Tensor([0.485,0.456,0.406])

    def make_heatmap(self,image, true_class, k=8, stride=8):
        image = self.normalize(image)

        heatmap = torch.zeros(int(((image.shape[2] - k) / stride) + 1), int(((image.shape[3] - k) / stride) + 1))
        image = image.data
        
        i = 0
        a = 0
        while i <= image.shape[3] - k:
            j = 0
            b = 0
            while j <= image.shape[2] - k:
                h_filter = torch.ones(image.shape)
                h_filter[:, :, j:j + k, i:i + k] = 0
                temp_image = Variable((image * h_filter))
                temp_softmax = self.model(temp_image)
                temp_softmax = torch.nn.functional.softmax(temp_softmax).data[0]
                heatmap[a][b] = temp_softmax[true_class]
                j += stride
                b += 1
            print(a)
            i += stride
            a += 1

        image = image.squeeze()

        true_image = image.transpose(0, 1)
        true_image = true_image.transpose(1, 2)

        true_image = self.deprocess(true_image)


        fig = plt.figure()
        plt.rcParams["figure.figsize"] = (20, 20)



        heatmap = heatmap - heatmap.min()
        
        heatmap = np.uint8(255 * heatmap)

        plt.imshow(heatmap)
        plt.show()
        

        return heatmap


