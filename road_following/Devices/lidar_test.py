import os
import sys
from pathlib import Path
from Lidar import LidarModule
import numpy as np
from Camera import CameraModule
import cv2
import time
lidar_module = LidarModule(lidar_port='/dev/ttyUSB1')
camera_module = CameraModule(width=640, height=480)
camera_module.open_cam(0)

car_detect_queue = 0
new_car_cnt = 0
obj = False
i = 0

detect_cnt = 0
while True:
    try:
        cam_img = camera_module.read()
        scan = np.array(lidar_module.iter_scans())
        print(scan)
        car_search_condition = (((50 < scan[:,0]) & (scan[:,0] < 60)) & (scan[:,1] < 300))
        if len(np.where(car_search_condition)[0]):
            car_detect_queue = (car_detect_queue * 2 + 1) % 32

        else:
            car_detect_queue = (car_detect_queue * 2) % 32

        if car_detect_queue == 0:
            
            if detect_cnt == 0:
                obj = False
                print('car not detected')
                pass
            else:
                detect_cnt -= 1
        else:
            if detect_cnt == 10:
                print('car detected')
                if obj == False:
                    new_car_cnt += 1
                obj = True
            else:
                detect_cnt += 1
        
        if new_car_cnt == 2:
            print("Detect two car!")
            break
        
        
        cv2.imshow("video", cam_img)
        print(i)
        i+=1
        if cv2.waitKey(25) == ord('f'):
            camera_module.close_cam()
            cv2.destroyAllWindows()
            
            lidar_module.lidar_finish()
            print("Program Finish")
            break
    except Exception as e:
        print("Error : {}".format(e))
        camera_module.close_cam()
        cv2.destroyAllWindows()
            
        lidar_module.lidar_finish()
        break
    
    except KeyboardInterrupt:
        print("Keyboard interrupt occur")
        camera_module.close_cam()
        cv2.destroyAllWindows()
            
        lidar_module.lidar_finish()
        break
    
    time.sleep(0.0001)
    
lidar_module.lidar_finish()
    
    