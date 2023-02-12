import sys
import os
from pathlib import Path
PATH = str(Path(os.path.dirname(os.path.abspath(__file__))).parent)
sys.path.append(PATH)
from utility import object_detection, box_area, box_center, center_inside, preprocess, show_bounding_box
from yolov5.models.common import DetectMultiBackend
from yolov5.utils.general import non_max_suppression
import cv2
from Algorithm.BirdEyeConverter import *
from utility import *

class avoidance():
    def __init__(self, serial, camera_module, detect_weight_file, speed):
        self.serial = serial
        self.front_camera_module = camera_module
        self.detect_weight_file = detect_weight_file
        self.detect_network = DetectMultiBackend(weights = self.detect_weight_file)
        self.speed = speed
        pass

    def action(self, outside_flag, day_evening):
        
        box_threshold = 15000
        while True:
            try:
                cam_img = self.front_camera_module.read()
                bird_img = bird_convert(cam_img, "FRONT")
                    # cv2.imshow("bird", bird_img)
                preprocess_img = total_function(bird_img, day_evening, "Mission")
                draw_img = cam_img.copy()
                image = preprocess(cam_img, "test", device = "cpu")
                pred = self.detect_network(image)
                pred = non_max_suppression(pred)[0]
                draw_img = show_bounding_box(draw_img, pred)
                detect, _, _ = object_detection(pred)
                car_bbox = detect[3]
                
                bbox_center = box_center(car_bbox)
                bbox_area = box_area(car_bbox)
                print(bbox_area)
                if outside_flag == True:
                    
                    if center_inside(bbox_center) == True and bbox_area > box_threshold:
                        direction = -7
                    else:
                        if center_inside2(bbox_center) == False:
                            break
                else:
                    if center_inside(bbox_center) == True and bbox_area > box_threshold:
                        direction = 7
                    else:
                        if center_inside2(bbox_center) == False:
                            break
                        
                message = "a" + str(direction) + "s" + str(self.speed)
                self.serial.write(message.encode())
            
                cv2.imshow('VideoCombined_detect', draw_img)
                cv2.imshow('VideoCombined_rf2', preprocess_img)

                pass
            except Exception as e:
                _, _, tb = sys.exc_info()
                print("avoidance error = {}, error line = {}".format(e, tb.tb_lineno))
                return False
                pass
            except KeyboardInterrupt:
                if self.front_camera_module:
                    print("Keyboard Interrupt occur")
                    self.front_camera_module.close_cam()
                    end_message = "a0s0"
                    self.serial.write(end_message.encode())
                    self.serial.close()
                break
                pass
                
            if cv2.waitKey(25) == ord('f'):
                end_message = "a0s0"
                self.serial.write(end_message.encode())
                self.serial.close()
                print(end_message)
                if self.front_camera_module:
                    self.front_camera_module.close_cam()
                    cv2.destroyAllWindows()
                
                print("Program Finish")
                
                break
