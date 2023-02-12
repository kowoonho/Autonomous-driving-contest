#
import cv2
import uuid
import time
import os
import glob
from bird_eye_utils import *

image_width = 640   # 640   864   
image_height = 360  # 480   480

imgs_path = '/home/zbpdh/GyeongJin/data_img/*.png'
imgs_list = glob.glob(imgs_path)

print(len(imgs_list))
img_idx = 0
for img_name in imgs_list:
    img = cv2.imread(img_name, cv2.IMREAD_COLOR)
    print(img_name[31])
    
    if (img_name[31] == 'f'):
        img_p = total_function(img, 'front')
    elif (img_name[31] == 'b'):
        img_p = total_function(img, 'back')
    
    cv2.imshow('img', img)
    cv2.imshow('proccessed', img_p)
    time.sleep(3)
    if cv2.waitKey(25) == ord('f') :
        break
