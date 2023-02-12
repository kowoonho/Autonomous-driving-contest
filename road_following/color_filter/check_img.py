import cv2
import numpy as np
import matplotlib.pyplot as plt
import pickle
import os
import glob
#from custom_code import *
#from Algorithm.img_preprocess import *
import sys
path_rf = os.path.dirname(os.path.dirname(__file__))
print(path_rf)
sys.path.append(path_rf)
from Algorithm.img_preprocess import *
from Algorithm.BirdEyeConverter import *
from utility import dominant_gradient
from utility import roi_cutting


#imgs = glob.glob("./img/*.png")
#imgs = glob.glob("../../../data_img/0115/*.png")
imgs = glob.glob("../no_green/*.png")

for inum ,iname in enumerate(imgs):
    while True:
        
        print(iname)
        img = cv2.imread(iname)
        
        bird_img = bird_convert(img, 'FRONT')
        preprocess_img = total_function(bird_img)
        binary_img = cvt_binary(bird_img)
        roi_img = roi_cutting(binary_img)
        
        draw_img = img.copy()

        cv2.imshow("bird_raw",bird_img)
        cv2.imshow("pre", preprocess_img)
        cv2.imshow("bin",binary_img)
        cv2.imshow("roi_img",roi_img)
        
        
        #img_stadium = total_function(img)
        img_gradient = dominant_gradient(preprocess_img, roi_img)
        #cv2.imshow('grad'+str(inum), img_gradient)
        cv2.imshow('original'+str(inum), img)

        
        if cv2.waitKey(1) & 0xFF == ord('f'):
            cv2.destroyAllWindows()
            break
