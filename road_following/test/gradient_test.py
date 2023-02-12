import os
import cv2
from utility import dominant_gradient

path = '../../data_img/0114/'

file_list = os.listdir(path)


if __name__ == '__main__':
    #print(file_list)
    for img_name in file_list:
        img = cv2.imread(path + img_name) 
        edge_img = dominant_gradient(img)
        cv2.imshow('img', img)
        cv2.imshow('edge_img', edge_img)
        cv2.waitKey()

