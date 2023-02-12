import random
import numpy as np
import os
import cv2
import PIL.Image
from torchvision import transforms
import sys
sys.path.append("/home/woonho/python/autonomous_driving/road_following")
from utility import return_augmented_images

num_augmented_images = 35000

file_path = "/hdd/woonho/autonomous_driving/rfdata/0113/"
file_names = os.listdir(file_path)
total_origin_image_num = len(file_names)
augment_cnt = 1

new_dir_path = "/hdd/woonho/autonomous_driving/rfdata/0113_aug/"
try:
    if not os.path.exists(new_dir_path):
        os.mkdir(new_dir_path)    
except OSError:
    print('Error: Creating dirctory. ' + new_dir_path)



for augment_cnt in range(1, num_augmented_images):
    change_picture_index = random.randrange(1, total_origin_image_num-1)
    file_name = file_names[change_picture_index]
    
    origin_image_path = os.path.join(file_path, file_name)
    print(origin_image_path)
    image = PIL.Image.open(origin_image_path)
    random_augment = random.randrange(1,4)
    augment_method = {1 : "noise", 2 : "brightness", 3 : "saturation"}
    
    augmented_image = return_augmented_images(image, style=augment_method[random_augment])
    
    augment_img_name = file_name[:-4] + augment_method[random_augment] + ".png"
    
    cv2.imwrite(os.path.join(new_dir_path, augment_img_name), augmented_image)
    print("Augmentation success : {}".format(augment_cnt))
        