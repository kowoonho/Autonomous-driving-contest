import torch
import glob
import os
from utility import get_resistance_value, preprocess, roi_cutting
import torch.nn.functional as F
import cv2
from Algorithm.img_preprocess import cvt_binary

class RFDataset(torch.utils.data.Dataset):
    
    def __init__(self, directory):
        self.directory = directory
        self.image_paths = glob.glob(os.path.join(self.directory, '*.png'))
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        
        image = cv2.imread(image_path)
        res_value = int(get_resistance_value(image_path)) + 7
        
        binary_image = cvt_binary(image)
        roi_image = roi_cutting(binary_image)
        tensor_image = preprocess(roi_image, mode="train")
        
        return tensor_image, F.one_hot(torch.tensor(res_value), num_classes=15) # classification
        # return tensor_image, torch.tensor(res_value, dtype=torch.float32)# regression
    
