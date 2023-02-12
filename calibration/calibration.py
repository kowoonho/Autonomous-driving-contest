import numpy as np
import cv2
import glob
import matplotlib.pyplot as plt
import time
import pickle
import os

path_cur = os.path.dirname(os.path.abspath(__file__))

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*8,3), np.float32)
objp[:,:2] = np.mgrid[0:8,0:6].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
images = glob.glob(path_cur + '/data_img_calib/*.png')
print(len(images))

for fname in images:
    img = cv2.imread(fname)
    if img is not None:
        # cv2.imshow('IMG', img)   # 읽은 이미지를 화면에 표시      
        # cv2.waitKey()           # 키가 입력될 때 까지 대기      
        # cv2.destroyAllWindows()  # 창 모두 닫기       
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        
        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (8,6), None)
        print(ret)
        
        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1), criteria)
            print(imgpoints)
            imgpoints.append(corners2)
            
            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, (8,6), corners2,ret)
            cv2.imshow('img',img)
            cv2.waitKey(500)
        
# 카메라 메트릭스, 왜곡 계수, 회전/이동 벡터
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
cv2.destroyAllWindows()

# print(mtx)
# print()
# print(rvecs)
# print()
# print(tvecs)

dic_param = {'mtx': mtx, 'coeff_dist': dist, 'rvecs': rvecs, 'tvecs': tvecs}
with open(path_cur + "/calib_param.pkl", 'wb') as f:
    pickle.dump(dic_param, f)

print(mtx)
with open(path_cur + '/calib_param.pkl', 'rb') as f: 
    dic_load = pickle.load(f)

# print('============================================')
# print('============================================')
# print("dictionary")
# print(dic_load['mtx'])
# print(dic_load['rvecs'])
# print(dic_load['tvecs'])
# print('============================================')
# print('============================================')

# 카메라 메트릭스를 최적화(개선)
img_sample = images[0]
img = cv2.imread(img_sample)
h, w = img.shape[:2]
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))

# 왜곡 제거
dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
x,y,w,h = roi
dst = dst[y:y+h, x:x+w]
cv2.imwrite(path_cur + '/calibresult.png',dst)
cv2.imshow('IMG', dst)   # 읽은 이미지를 화면에 표시      
cv2.waitKey()           # 키가 입력될 때 까지 대기      
cv2.destroyAllWindows()  # 창 모두 닫기 

tot_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv2.norm(imgpoints[i],imgpoints2, cv2.NORM_L2)/len(imgpoints2)
    tot_error += error
print("total error: ", tot_error/len(objpoints))
