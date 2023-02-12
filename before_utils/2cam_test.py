import cv2
import uuid
from bird_eye_utils import *
import os

image_width = 640   # 640   864   
image_height = 360  # 480   480

cap_f = cv2.VideoCapture(2)     ###
cap_f.set(cv2.CAP_PROP_FRAME_WIDTH, image_width)      # 864
cap_f.set(cv2.CAP_PROP_FRAME_HEIGHT, image_height)     # 480

cap_b = cv2.VideoCapture(4)     ###
cap_b.set(cv2.CAP_PROP_FRAME_WIDTH, image_width)      # 864
cap_b.set(cv2.CAP_PROP_FRAME_HEIGHT, image_height)     # 480

print(cv2.__version__) 
print(cap_f.isOpened())
print(cap_b.isOpened())

# FPS 확인
fps_f = cap_f.get(cv2.CAP_PROP_FPS)     
print('fps front', fps_f)
fps_b = cap_b.get(cv2.CAP_PROP_FPS)     
print('fps back', fps_b)


img_idx = 0
while img_idx < 30:
    ret_f, frame_f = cap_f.read()
    ret_b, frame_b = cap_b.read()
    if img_idx == 0:
        print(frame_f.shape)
        img_idx = 1
    if (ret_f is True) and (ret_b is True):
        # print(frame.shape)
        cv2.imshow('frame_f', frame_f)
        # frame_f_p = total_function(frame_f, 'front')
        # cv2.imshow('processed', frame_f_p)
        
        cv2.imshow('frame_b', frame_b)
        # frame_b_p = total_function(frame_b, 'back')
        # cv2.imshow('processed', frame_b_p)

        if cv2.waitKey(25) == ord('f') :
            break
