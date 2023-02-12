import os
import sys
sys.path.append("/Users/yunsu/Desktop/대학자료/Autonomous Driving(MIDASL)/code/1st-AD-SW-Competition/road_following")
from Dataset.parking_constant import Parking_constant


park = Parking_constant()


for i in range(100):
    park.car_detect_queue = i
    print(park.car_detect_queue)