import cv2
import uuid
import time
import os

from bird_eye_utils import *

image_width = 640   # Hyper Para : (640,360)  (640,480)  (864,480)   
while True:
    cam_name = input("Enter Camera Name (f:Front, r:Rear) : ")
    if cam_name == 'f':
        cam_idx = 2
        image_height = 480
        cam_name = "FRONT"
        break
    elif cam_name == 'r':
        cam_idx = 4
        image_height = 360 
        cam_name = "REAR"
        break
    else:
        print("Wrong Camera")


# cap = cv2.VideoCapture('/dev/video2')
# cap = cv2.VideoCapture(2, cv2.CAP_V4L2)   # CAP_DSHOW : Microsoft, CAP_V4L2 : Linux
cap = cv2.VideoCapture(cam_idx)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, image_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, image_height)
print(cv2.__version__) 
print(cap.isOpened())

fps = cap.get(cv2.CAP_PROP_FPS)     # FPS 확인
print('fps', fps)

img_idx = 0
while True:
    ret, frame = cap.read()
    if img_idx == 0:
        print(type(frame))
        print(frame.shape)
        img_idx = 1
    if (ret is True):
        cv2.imshow('frame', frame)
        frame_p = bird_convert(frame, cam_name)
        cv2.imshow('processed', frame_p)

        if cv2.waitKey(25) == ord('f') :
            break

cv2.destroyAllWindows()
cap.release()