import os
import sys
from pathlib import Path
PATH = str(Path(os.path.dirname(os.path.abspath(__file__))).parent)
sys.path.append(PATH)
import serial
from Devices.Camera import CameraModule
import time
import keyboard
import cv2

class LogCollection():
    def __init__(self, cam_name, txt_path):
        self.camera_module = None
        self.cam_num = {"FRONT" : 2, "REAR" : 4}
        self.cam_name = cam_name
        self.txt_path = txt_path
        
        self.serial = serial.Serial()
        self.serial.port = '/dev/ttyUSB0'       ### 아두이노 메가
        self.serial.baudrate = 9600
        self.speed = 0
        self.direction = 0
        self.brk = 0
        
    def serial_start(self):
        try:
            self.serial.open()
            print("Serial open")
            time.sleep(1)
            return True
        
        except Exception as _:
            print("Serial Fail")
            return False
    
    def camera_start(self):
        try:
            self.camera_module = CameraModule(width=640, height=480)
            self.camera_module.open_cam(self.cam_num[self.cam_name])
            print("FRONT Camera open")
            return True
        
        except Exception as _:
            print("FRONT Camera Fail")
            return False
        
    def control_direction(self, input_key):
        self.brk = 0     # loop break
        if input_key == 'f':
            self.direction = 0
            self.speed = 0
            print('program finish')
            self.brk = 1
        elif input_key == 'w': # start
            print('you pressed w')
            self.speed = 50
            self.direction = 0
        elif input_key == 'a':#좌진
            print('you pressed a')
            self.direction -= 1
        elif input_key == 'd':#우진
            print('you pressed d')
            self.direction += 1 
        elif input_key == 's':
            self.direction = 0   # stop
            self.speed = 0

        if(self.direction < -7):
            self.direction = -7
        elif (self.direction > 7):
            self.direction = 7  
        pass
    
    def collection(self):
        keys = ['w', 'a', 's', 'd', 'f']
        f = open(self.txt_path, 'w')
        while True:
            try:
                if self.camera_module == None:
                    print("Please Check Camera module")
                    break
                    pass
                else:
                    for k in keys:
                        if keyboard.is_pressed(k):
                            input_key = k
                    self.control_direction(input_key)
                    
                    if self.brk == 1:
                        break
                    message = 'a' + str(self.direction) + 's' + str(self.speed)
                    self.serial.write(message.encode())
                    print(message)
                    
                    if self.speed != 0:
                        f.write(message + '\n')
                    
                    
                    pass
            except Exception as e:
                if self.camera_module:
                    print("Exception in process")
                    self.camera_module.close_cam()
                    end_message = "a0s0"
                    self.serial.write(end_message.encode())
                    self.serial.close()
                    f.close()
                break
                pass
            except KeyboardInterrupt:
                if self.camera_module:
                    print("Keyboard Interrupt occur")
                    self.camera_module.close_cam()
                    end_message = "a0s0"
                    self.serial.write(end_message.encode())
                    self.serial.close()
                    f.close()
                break
                pass
            
            if cv2.waitKey(10) == ord('f') :
                if self.camera_module:
                    self.camera_module.close_cam()
                    cv2.destroyAllWindows()
                end_message = "a0s0"
                self.serial.write(end_message.encode())
                self.serial.close()
                print("Program Finish")
                f.close()
                break
                
            time.sleep(0.0001)
        
    
if __name__ == '__main__':
    LOG_DIR_PATH = os.path.join(PATH, "log_data")
    try:
        if not os.path.exists(LOG_DIR_PATH):
            os.mkdir(LOG_DIR_PATH)    
    except OSError:
        print('Error: Creating dirctory. ' + LOG_DIR_PATH)
    FILE_NAME = sys.argv[1]
    
    
    processor = LogCollection("FRONT", os.path.join(LOG_DIR_PATH, FILE_NAME))
    serial_result = processor.serial_start()
    if serial_result:
        cam_opened = processor.camera_start()
        if cam_opened:
            print("Log Collection Start")
            processor.collection()
    
    
    
    pass