### custom_code.py 수정

import cv2
import numpy as np
import matplotlib.pyplot as plt
import pickle
import os

direction_div = 12
'''
### roi
_shape = np.array([
    [(int(0.05 * image_width), int(0.20 * image_height)), (int(0.495 * image_width), int(0.20 * image_height)), 
    (int(0.495 * image_width), int(0.95 * image_height)), (int(0.05 * image_width), int(0.95 * image_height))], 
    [(int(0.505 * image_width), int(0.20 * image_height)), (int(0.95 * image_width), int(0.20 * image_height)), 
    (int(0.95 * image_width), int(0.95 * image_height)), (int(0.505 * image_width), int(0.95 * image_height))]
    ])
    
## srcmat 예시
mat_pts_src = np.float32([[263, 31], [582, 47], [557, 349], [8, 250]])  ###
'''

# Source Points of Front / Back Camera
def which_srcmat(FB):
    dic_param = {}
    if FB == 'FRONT':
        path_perspect = os.path.dirname(os.path.abspath(__file__))
        with open(path_perspect + '/front_perspect_param.pkl', 'rb') as f:
            # print('perspect.pkl opened!')   
            dic_param = pickle.load(f)
    elif FB == 'REAR':
        path_perspect = os.path.dirname(os.path.abspath(__file__))
        with open(path_perspect + '/back_perspect_param.pkl', 'rb') as f:   
            # print('perspect.pkl opened!')   
            dic_param = pickle.load(f)
            
    if len(dic_param) != 0:
        return dic_param['pts_src']
    else:
        return None
    
    
# Warpping (Bird Eye View)
def warpping(image, pts_src, FB):
    (h, w) = (image.shape[0], image.shape[1])
    ###source = np.float32([[223, 349], [461, 336], [622, 426], [102, 445]])
    if FB == "FRONT":
        destination = np.float32(
            [[round(w * 0.3), round(h * 0.0)], [round(w * 0.7), round(h * 0.0)], 
            [round(w * 0.7), h], [round(w * 0.3), h]])
    elif FB == "REAR":
        destination = np.float32(
            [[round(w * 0.2), round(h * 0.15)], [round(w * 0.8), round(h * 0.15)], 
            [round(w * 0.8), round(h * 1.0)], [round(w * 0.2), round(h * 1.0)]])
    transform_matrix = cv2.getPerspectiveTransform(pts_src, destination)
    minv = cv2.getPerspectiveTransform(destination, pts_src)
    _image = cv2.warpPerspective(image, transform_matrix, (w,h))

    return _image, minv


def bird_convert(img, FB):
    srcmat = which_srcmat(FB)
    img_warpped, minverse = warpping(img, srcmat, FB)

    # cv2.imshow('warp', img_warpped)    ###
    
    return img_warpped

