import os
import cv2
import torch
from Networks.model import ResNet18
from utility import get_resistance_value, preprocess
import argparse
from pathlib import Path
import sys

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.abspath(ROOT))

test_file_dir_path = ""
weight_file = "./model_weight_file/best_steering_model_0115a.pth"

img_list = os.listdir(test_file_dir_path)
list_size = len(img_list)

model = ResNet18(weight_file=weight_file)

answer_cnt = 0

print("Predict Start!")
print("---------------------")

for image in img_list:
    res_value = get_resistance_value(image)
    
    img = cv2.imread(os.path.join(test_file_dir_path, image))
    preprocess_img = preprocess(img, mode = "test")
    pred = torch.argmax(model.run(preprocess_img)) - 7
    
    
    score = 1 - abs(res_value - pred) / 14
    answer_cnt += score
    
    # if res_value == pred:
    #     answer_cnt += 1

accuracy = (answer_cnt / list_size) * 100

print("Accuracy : {}%".format(accuracy))
