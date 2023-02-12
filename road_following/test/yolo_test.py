import cv2
import os
import sys
import torch
import numpy as np
from glob import glob
import matplotlib.pyplot as plt
from pathlib import Path
PATH = os.pardir
sys.path.append(PATH)
print(sys.path)
from yolov5.models.common import DetectMultiBackend
from yolov5.utils.general import non_max_suppression
from utility import preprocess, show_bounding_box
labels_to_names = {0 : "Crosswalk", 1 : "Green", 2 : "Red", 3 : "Car"}

weight_file_path = os.path.join(PATH, 'model_weight_file', 'yolo_final_weight.pt')
model = DetectMultiBackend(weights = weight_file_path)

img_path = os.path.join(PATH, 'test_image')
img_list = glob(os.path.join(img_path, "car*"))


device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)

for i in range(5):
    img = cv2.imread(img_list[i])
    draw_img = img.copy()
    image = preprocess(img, 'test').cpu()
    pred = model(image)
    pred = non_max_suppression(pred)[0]
    
    draw_img, detect_list = show_bounding_box(draw_img, pred)
    
    plt.subplot(1, 5, i+1)
    plt.imshow(draw_img)

plt.show()
