#!/usr/bin/env python
import traceback

import cv2
import sys
import argparse
import os
import numpy as np
from Processor import Processor

# setup tensorrt weight file pass
processor = Processor(model='test.trt')
x1, y1, x2, y2 = 0,0,0,0
score = 0.0
def Detect_Mark(image):
    """
        box : [x1,y1,x2,y2]
        center_x : center of bounding box(x)
        center_y : center of bounding box(y)
        confs : score
        overlay : result image
        width : width of bounding box
    """
    global x1
    global y1
    global x2
    global y2
    global score
    box = []
    center_x = 0
    center_y = 0
    confs = 0
    overlay = []

    # inference
    output = processor.detect(image)
    resized_img = cv2.resize(image, (640, 640))
    try:
        # boxes = processor.extract_boxes(output)
        boxes = processor.extract_boxes(output)
        overlay = resized_img.copy()

        # Transforms raw output into boxes, score, classes
        boxes, confs, classes = processor.post_process(output)
        for box in boxes:
            x1,y1,x2,y2 = box
            score = np.max(confs)
        return True, [x1, y1], score, overlay.shape[1], overlay

    except Exception as e:
        print('ML Module Run Error = ', e)
        print('ML Module Error line = ', traceback.format_exc())
        return False, [-1, -1], -1, [], None