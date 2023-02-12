import numpy as np
from dataclasses import dataclass
# @dataclass
class Parking_constant():
    # detect_cnt:int = 0
    # new_car_cnt:int = 0
    # obj:bool = False
    # queue_key:int = 0
    # total_array = np.array([[-1, -1, -1]])
    def __init__(self):
        self.detect_cnt = 0
        self.not_detect_cnt = 0
        self.new_car_cnt = 0
        self.angle = 0
        self.obj = 0
        self.queue_key = 0
        self.total_array = np.array([[-1, -1, -1]])
        self.flag = False
        self.stop = False
        
    def initialize(self):
        self.detect_cnt = 0
        self.not_detect_cnt = 0
        self.new_car_cnt = 0
        self.angle = 0
        self.obj = 0
        self.queue_key = 0
        self.total_array = np.array([[-1, -1, -1]])
        self.flag = False
        self.stop = False