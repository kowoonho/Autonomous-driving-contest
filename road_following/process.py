import Devices.Camera
import Devices.rplidar
from Algorithm.BirdEyeConverter import *
from Networks import model
import serial
import time
import torch
import torchvision.transforms as transform
import sys
rf_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(rf_dir, "yolov5"))
from yolov5.models.common import DetectMultiBackend
from yolov5.utils.general import non_max_suppression
from utility import *
from Algorithm.parking_2 import *
from Algorithm.Control import total_control, smooth_direction, strengthen_control
from Algorithm.img_preprocess import total_function, total_function_parking
from Algorithm.object_avoidance import avoidance
from Algorithm.ideal_parking import idealparking
from Devices.Lidar import LidarModule
from Dataset.parking_constant import Parking_constant
class DoWork:
    def __init__(self, play_name, front_cam_name, rear_cam_name, rf_weight_file = None, detect_weight_file = None,
                  driving_type = None, parking_stage = None, speed_value = None):
        self.play_type = play_name
        
        # Camera
        self.front_camera_module = None
        self.rear_camera_module = None
        self.cam_num = {"FRONT" : 2, "REAR" : 4}
        self.front_cam_name = front_cam_name
        self.rear_cam_name = rear_cam_name
        
        # Model
        self.rf_weight_file = rf_weight_file
        self.detect_weight_file = detect_weight_file

        # self.rf_network = model.ResNet18(weight_file = self.rf_weight_file) if play_name == "Driving" else None
        self.detect_network = DetectMultiBackend(weights = detect_weight_file)
        self.labels_to_names = {0 : "Crosswalk", 1 : "Green", 2 : "Red", 3 : "Car"}
        
        # Arduino Serial
        self.serial = serial.Serial()
        self.serial.port = '/dev/ttyUSB0'       ### 아두이노 메가
        self.serial.baudrate = 9600
        
        # Control
        
        self.speed_value = int(speed_value)
        self.speed = int(speed_value)
        
        self.direction = 0
        
        # Lidar
        self.lidar_port = '/dev/ttyUSB1'
        self.lidar_module = None
        
        # Driving type
        self.driving_type = driving_type
        if play_name == "Parking":
            self.parking_stage = int(parking_stage)

        # Weather value
        self.day_evening_value = 155
        """
        day 200, 190, 180, 170, 165, 155 evening
        """
        # Parking value
        self.near_detect_value = 600

    def serial_start(self):
        try:
            self.serial.open()
            print("Serial open")
            time.sleep(0.5)
            return True
        
        except Exception as e:
            _, _, tb = sys.exc_info()
            print("serial start error = {}, error line = {}".format(e, tb.tb_lineno))
            return False
    
    def front_camera_start(self):
        try:
            self.front_camera_module = Devices.Camera.CameraModule(width=640, height=480)
            self.front_camera_module.open_cam(self.cam_num[self.front_cam_name])
            print("FRONT Camera open")
            return True
        
        except Exception as e:
            _, _, tb = sys.exc_info()
            print("front camera start error = {}, error line = {}".format(e, tb.tb_lineno))
            return False
        
    def rear_camera_start(self):
        try:
            self.rear_camera_module = Devices.Camera.CameraModule(width=640, height=360)
            self.rear_camera_module.open_cam(self.cam_num[self.rear_cam_name])
            print("REAR Camera open")
            return True
        
        except Exception as e:
            _, _, tb = sys.exc_info()
            print("rear camera start error = {}, error line = {}".format(e, tb.tb_lineno))
            return False
        
    def lidar_start(self):
        try:
            self.lidar_module = LidarModule()
            print("Lidar open")
            return True
        except Exception as e:
            _, _, tb = sys.exc_info()
            print("lidar start error = {}, error line = {}".format(e, tb.tb_lineno))
            return False    

    def Driving(self):
        bef_1d, bef_2d, bef_3d= 0,0,0
        day_evening = self.day_evening_value
        while True:
            try:
                if self.front_camera_module == None:
                    print("Please Check Camera module")
                    break
                    pass
                else:
                    cam_img = self.front_camera_module.read()
                    bird_img = bird_convert(cam_img, self.front_cam_name)
                    # cv2.imshow("bird", bird_img)
                    preprocess_img = total_function(bird_img, day_evening, self.driving_type)
                    binary_img = cvt_binary(preprocess_img)
                    # roi_img = roi_cutting(binary_img)
                    
                    draw_img = cam_img.copy()

                    
                    order_flag = 1
                    
                    if self.detect_weight_file != None: # Detection 했을 경우
                        image = preprocess(cam_img, "test", device = "cpu")
                        pred = self.detect_network(image)
                        pred = non_max_suppression(pred)[0]
                        
                        pred = distinguish_traffic_light(draw_img, pred)
                        if self.driving_type == "Mission":
                            draw_img = show_bounding_box(draw_img, pred)

                        detect, order_flag, is_crosswalk = object_detection(pred)

                        if self.driving_type == "Time":
                            order_flag = 1
                    
                    roi_img1 = roi_cutting(binary_img, 250)
                    roi_img2 = roi_cutting(binary_img, 150)

                        
                    _, bottom_value = dominant_gradient(roi_img1)
                    road_gradient, _ = dominant_gradient(roi_img2)

                    

                    if (road_gradient == None and bottom_value == None): # Gradient가 없을 경우 예외처리(Exception Image)
                        self.direction = 0
                        message = 'a' + str(bef_1d) +  's' + str(self.speed)
                        self.serial.write(message.encode())
                        #print(message)
                        continue    
                    if is_crosswalk == True:
                        day_evening = self.day_evening_value
                        # road_direction = return_road_direction(road_gradient)
                        # print(road_gradient)
                        # print(road_direction)
                        # final_direction = road_direction
                        if detect[1] != None:
                            final_direction = int(box_control(detect[1]))
                        elif detect[2] != None:
                            final_direction = int(box_control(detect[2]))
                        else:
                            final_direction = 0
                        #print(final_direction)
                    else:
                        
                        road_direction = return_road_direction(road_gradient)
                        final_direction = strengthen_control(road_direction, road_gradient, bottom_value)
                        


                    # print('grad: ',road_gradient)
                    # print('bottom: ', bottom_value)
                    
                    # model_direction = torch.argmax(self.rf_network.run(preprocess(roi_img, mode = "test"))).item() - 7
                    # final_direction = total_control(road_direction, model_direction, bottom_value)
                    
                    if order_flag == 0: # stop
                        self.direction = 0
                        self.speed = 0
                        
                        pass
                    elif order_flag == 1: # go
                        # self.direction = final_direction
                        self.speed = self.speed_value
                        self.direction = smooth_direction(bef_1d, bef_2d, bef_3d, final_direction)
                        # print("go")
                        pass
                    
                    elif order_flag == 2: # road change
                        print("road change!")
                        day_evening = self.day_evening_value + 10
                        avoidance_processor = avoidance(self.serial, self.front_camera_module, 
                                                        self.detect_weight_file, 50)
                        avoidance_processor.action(is_outside(preprocess_img), day_evening)

                    # if self.driving_type == "Time":
                        # if abs(self.direction) >= 4:
                            # self.speed -= 10 * (abs(self.direction) - 4)

                    
                        # if self.direction >=4 and self.direction <=6:
                        #     # self.direction +=1
                        #     self.speed -= 20
                    message = 'a' + str(self.direction) +  's' + str(self.speed)
                    self.serial.write(message.encode())
                    #print(message)
                    
                    # cv2.imshow('VideoCombined_detect', draw_img)
                    # cv2.imshow('VideoCombined_rf', roi_img)
                    cv2.imshow('VideoCombined_rf2', preprocess_img)
                    
                    bef_1d, bef_2d, bef_3d = final_direction, bef_1d, bef_2d
                    pass
                
            except Exception as e:
                if self.front_camera_module:
                    _, _, tb = sys.exc_info()
                    print("process error = {}, error line = {}".format(e, tb.tb_lineno))
                    self.front_camera_module.close_cam()
                    end_message = "a0s0"
                    self.serial.write(end_message.encode())
                    self.serial.close()
                break
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
            
            time.sleep((0.0001))
    
    def Parking(self):
        """
        1. Search Parking location
        => 잠깐 정지 후에 Parking Position 연산 => 대표값으로 연산
        2. Ideal Parking Position
        3. Action
        """
        
        # parking_direction = 0
        parking_speed = self.speed_value
        self.parking_speed = parking_speed
        distance_threshold = 250
        bef_stage = self.parking_stage-1
        
        constant = Parking_constant()
        print(constant.new_car_cnt)
        while True:
            try:
                if self.front_camera_module == None:
                    print("Please Check Camera module")
                    break
                    pass
                if self.lidar_module == None:
                    print("Please Check Lidar module")
                    break
                    pass
                front_cam_img = self.front_camera_module.read()
                if bef_stage != self.parking_stage:
                    print("Parking stage : {}".format(self.parking_stage))
                print("Parking stage : ", self.parking_stage)

                
                if self.parking_stage == -1: # Lidar Test
                    # 
                    self.parking_speed = 0
                    scan = np.array(self.lidar_module.iter_scans())
                    condition = lidar_condition(-110, 110, 2000, scan)
                    print(scan[np.where(condition)])
                    # scan = scan[lidar_condition(-180, 180, 2000, scan)]

                    

                    pass
                
                if self.parking_stage == 0:
                    stay_with_lidar(self.lidar_module, self.serial, speed = parking_speed, direction = 0,
                                    rest_time=2)
                    self.parking_stage = 1
                    constant.initialize()

                if self.parking_stage == 1: # Search parking start position
                    self.parking_speed = parking_speed
                    self.direction = 0 # 선 따라가도록 바꿀 예정
                    
                    constant = detect_parking_car(self.lidar_module, constant)
                    # print(constant.obj)
                    print("New car cnt : ",constant.new_car_cnt)
                    if constant.new_car_cnt == 2:
                        print("Detect two car!")
                        stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 7)
                        self.parking_stage = 2
                        constant.initialize()

                    
                    
                    
                elif self.parking_stage == 2:
                    self.parking_speed = -1 * parking_speed
                    self.direction = 7
                    
                    if near_detect_car(self.lidar_module, self.near_detect_value) == True:
                        stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                        constant.initialize()
                        self.parking_stage = 3
                    pass
                
                elif self.parking_stage == 3:
                    self.direction = 0
                    self.parking_speed = parking_speed
                    # if escape(self.lidar_module) == True:
                    #     stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                    #     constant.initialize()
                    #     self.parking_stage = 3

                    stay_with_lidar(self.lidar_module, self.serial, speed = parking_speed,
                                     direction = 0, rest_time=5)
                    
                    stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)

                    constant.initialize()
                    self.parking_stage = 4
                elif self.parking_stage == 4:
                    self.direction, constant= steering_parking(self.lidar_module, constant,left_direction=45)
                    
                    self.parking_speed = parking_speed * -1
                    
                    constant.queue_key = (constant.queue_key + 1) % 10
                    if near_detect_car(self.lidar_module, self.near_detect_value) == True:
                        constant = search_left_right(self.lidar_module, constant)
                        if constant.flag == True:

                            print("Search_left_right")

                            # calculate distance
                            stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = self.direction,
                                            rest_time=0.5)
                            
                            left_dist, right_dist = calculate_distance(self.lidar_module)
                            f = lambda x, y : abs(x - y)
                            if(f(left_dist, right_dist) > distance_threshold):
                                constant.initialize()
                                stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                                self.parking_stage = 5
                            else:
                                stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                                self.parking_stage = 10
                                
                                constant.initialize()
                                constant.detect_cnt = 3


                        stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                        constant.initialize()
                        self.parking_stage = 5

                    constant = search_left_right(self.lidar_module, constant)
                    if constant.flag == True:

                        print("Search_left_right")

                        # calculate distance
                        stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = self.direction,
                                        rest_time=0.5)
                        
                        left_dist, right_dist = calculate_distance(self.lidar_module)
                        f = lambda x, y : abs(x - y)
                        if(f(left_dist, right_dist) > distance_threshold):
                            constant.initialize()
                            stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                            self.parking_stage = 5
                        else:
                            stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                            self.parking_stage = 10
                            
                            constant.initialize()
                            constant.detect_cnt = 5
                
                elif self.parking_stage == 5:
                    self.direction = 0
                    self.parking_speed = parking_speed
                    # if escape(self.lidar_module) == True:
                    #     stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                    #     constant.initialize()
                    #     self.parking_stage = 3

                    stay_with_lidar(self.lidar_module, self.serial, speed = parking_speed,
                                     direction = 0, rest_time=5)
                    stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                    

                    constant.initialize()
                    self.parking_stage = 6

                elif self.parking_stage == 6:
                    self.direction, constant= steering_parking(self.lidar_module, constant, left_direction = 60)
                    
                    self.parking_speed = parking_speed * -1
                    
                    constant.queue_key = (constant.queue_key + 1) % 10
                    if near_detect_car(self.lidar_module, self.near_detect_value) == True:

                        constant = search_left_right(self.lidar_module, constant)
                        if constant.flag == True:

                            print("Search_left_right")

                            # calculate distance
                            stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = self.direction,
                                            rest_time=0.5)
                            
                            left_dist, right_dist = calculate_distance(self.lidar_module)
                            f = lambda x, y : abs(x - y)
                            if(f(left_dist, right_dist) > distance_threshold):
                                constant.initialize()
                                stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                                self.parking_stage = 7
                            else:
                                stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                                self.parking_stage = 10
                                
                                constant.initialize()
                                constant.detect_cnt = 5
                        stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                        constant.initialize()
                        self.parking_stage = 7

                    constant = search_left_right(self.lidar_module, constant)
                    if constant.flag == True:

                        print("Search_left_right")

                        # calculate distance
                        stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = self.direction,
                                        rest_time=0.5)
                        
                        left_dist, right_dist = calculate_distance(self.lidar_module)

                        if(abs(left_dist - right_dist) > distance_threshold):
                            constant.initialize()
                            stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                            self.parking_stage = 7
                        else:
                            stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                            self.parking_stage = 10
                            
                            constant.initialize()
                            constant.detect_cnt = 5

                elif self.parking_stage == 7:
                    self.direction = 0
                    self.parking_speed = parking_speed
                    # if escape(self.lidar_module) == True:
                    #     stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                    #     constant.initialize()
                    #     self.parking_stage = 3

                    stay_with_lidar(self.lidar_module, self.serial, speed = parking_speed,
                                     direction = 0, rest_time=5)
                    stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                    

                    constant.initialize()
                    self.parking_stage = 8


                

                
                elif self.parking_stage == 8:
                    self.direction, constant= steering_parking(self.lidar_module, constant, left_direction = 100)
                    
                    self.parking_speed = parking_speed * -1
                    
                    constant.queue_key = (constant.queue_key + 1) % 10
                    if near_detect_car(self.lidar_module, self.near_detect_value) == True:

                        constant = search_left_right(self.lidar_module, constant)
                        if constant.flag == True:

                            print("Search_left_right")

                            # calculate distance
                            stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = self.direction,
                                            rest_time=0.5)
                            
                            left_dist, right_dist = calculate_distance(self.lidar_module)
                            f = lambda x, y : abs(x - y)
                            if(f(left_dist, right_dist) > distance_threshold):
                                constant.initialize()
                                stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                                self.parking_stage = 9
                            else:
                                stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                                self.parking_stage = 10
                                
                                constant.initialize()
                                constant.detect_cnt = 5
                        stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                        constant.initialize()
                        self.parking_stage = 9

                    constant = search_left_right(self.lidar_module, constant)
                    if constant.flag == True:

                        print("Search_left_right")

                        # calculate distance
                        stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = self.direction,
                                        rest_time=0.5)
                        
                        left_dist, right_dist = calculate_distance(self.lidar_module)

                        if(abs(left_dist - right_dist) > distance_threshold):
                            constant.initialize()
                            stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                            self.parking_stage = 9
                        else:
                            stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                            self.parking_stage = 10
                            
                            constant.initialize()
                            constant.detect_cnt = 5

                elif self.parking_stage == 9:
                    self.direction = 0
                    self.parking_speed = parking_speed

                    stay_with_lidar(self.lidar_module, self.serial, speed = parking_speed,
                                     direction = 0, rest_time=5)
                    stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                    

                    constant.initialize()
                    self.parking_stage = 8 
                
                elif self.parking_stage == 10:
                    self.parking_speed = -1 * parking_speed


                    self.direction = 0
                    constant = stop(self.lidar_module, constant)
                    print("Stop_cnt : ",constant.detect_cnt)
                    if constant.flag == False:
                        constant.initialize()
                        stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0, rest_time=3)
                        self.parking_stage = 11

                elif self.parking_stage == 11:
                    self.parking_speed = parking_speed
                    self.direction = 0
                    
                    constant = escape_parking(self.lidar_module, constant)
                    print("detect_cnt :",constant.detect_cnt)
                    if constant.flag == True:
                        constant.initialize()
                        stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = -7)
                        self.parking_stage = 12
                
                elif self.parking_stage == 12:
                    self.parking_speed = parking_speed
                    self.direction = -7

                    stay_with_lidar(self.lidar_module, self.serial, speed = parking_speed, direction = -7, rest_time=12.5)


                    constant.initialize()
                    stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                    self.parking_stage = 13
                
                elif self.parking_stage == 13:
                    self.parking_speed = parking_speed
                    self.direction = 0

                    stay_with_lidar(self.lidar_module, self.serial, speed = parking_speed, direction = 0, rest_time=9)


                    constant.initialize()
                    stay_with_lidar(self.lidar_module, self.serial, speed = 0, direction = 0)
                    self.parking_stage = 14
                    
                elif self.parking_stage == 14:
                    self.parking_speed = 0
                    self.direction = 0
                    
                    constant.initialize()

                    if self.front_camera_module:
                        self.front_camera_module.close_cam()
                        cv2.destroyAllWindows()
                    if self.lidar_module:
                        self.lidar_module.lidar_finish()
                    
                    end_message = "a0s0"
                    self.serial.write(end_message.encode())
                    self.serial.close()

                    print("Program finish")
                    break




                    


                

                message = 'a' + str(self.direction) +  's' + str(self.parking_speed)
                # print(message)
                self.serial.write(message.encode())
                
                
                    
                
                cv2.imshow("video_original_f", front_cam_img)
                
                bef_stage = self.parking_stage
                
                
            except Exception as e:
                if self.front_camera_module:
                    print("Exception occur")
                    self.front_camera_module.close_cam()
                    cv2.destroyAllWindows()
                if self.lidar_module:
                    self.lidar_module.lidar_finish()
                _, _, tb = sys.exc_info()
                print("process error = {}, error line = {}".format(e, tb.tb_lineno))
                end_message = "a0s0"
                self.serial.write(end_message.encode())
                self.serial.close()
                break
                pass
            
            except KeyboardInterrupt:
                if self.front_camera_module:
                    print("Keyboard Interrupt occur")
                    self.front_camera_module.close_cam()
                    cv2.destroyAllWindows()
                if self.lidar_module:
                    self.lidar_module.lidar_finish()
                end_message = "a0s0"
                self.serial.write(end_message.encode())
                self.serial.close()
                
                break
                pass
            
            if cv2.waitKey(25) == ord('f') :
                if self.front_camera_module:
                    self.front_camera_module.close_cam()
                    cv2.destroyAllWindows()
                if self.lidar_module:
                    self.lidar_module.lidar_finish()
                end_message = "a0s0o0"
                self.serial.write(end_message.encode())
                self.serial.close()
                self.lidar_module.lidar_finish()
                print("Program Finish")
                
                break
            
            # time.sleep((0.00001))
        pass
                
                
        
        
