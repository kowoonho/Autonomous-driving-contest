import os
import sys
import cv2
sys.path.append("/home/woonho/python/autonomous_driving/road_following")
from utility import roi_cutting

img_path = "/hdd/woonho/autonomous_driving/rfdata/0108a_bev"

img_list = os.listdir(img_path)

new_dir_path = "/hdd/woonho/autonomous_driving/rfdata/0108a_roi_bev"
try:
    if not os.path.exists(new_dir_path):
        os.mkdir(new_dir_path)    
except OSError:
    print('Error: Creating dirctory. ' + new_dir_path)

img_cnt = 1
for img_name in img_list:
    img = cv2.imread(os.path.join(img_path, img_name))
    roi_img = roi_cutting(img)
    new_img_name = img_name[:-4] + "--roi--" + ".png"
    
    cv2.imwrite(os.path.join(new_dir_path, new_img_name), roi_img)
    
    print("Fininsh {} image roi cutting".format(img_cnt))
    img_cnt += 1
    
    


