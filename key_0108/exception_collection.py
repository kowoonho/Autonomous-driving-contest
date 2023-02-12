'''
키 조작

w : 속도 +1
s : 속도 -1
a : 회전 -1     (- : 좌회전, + : 우회전)
d : 회전 +1

r : 일시정지
f : 종료
'''


# from socket import *
import string
import keyboard
import time
import serial
import cv2
import time
import uuid
import os
import sys

path_project = os.path.dirname(os.path.dirname(__file__))
print(path_project)
sys.path.append(path_project)
sys.path.append("/home/skkcar/Desktop/contest/1st-AD-SW-Competition_0114/road_following/")
from before_utils.bird_eye_utils import *
from road_following.Algorithm.img_preprocess import total_function as total
from road_following.Algorithm.img_preprocess import cvt_binary
# Functions
def dir_and_speed(input_key, direction, speed):
    brk = 0     # loop break
    if input_key == 'f':
        direction = 0
        speed = 0
        print('program finish')
        brk = 1
    elif input_key == 'w':#직진
        print('you pressed w')
        speed += 10
    elif input_key == 'a':#좌진
        print('you pressed a')
        direction -= 1
    elif input_key == 'd':#우진
        print('you pressed d')
        direction += 1 
    elif input_key == 's':#후진
        print('you pressed s')
        speed -= 10
    elif input_key == 'r':#stop
        print('you pressed r')
        direction = 0
        speed = 0
    elif input_key == 's':
        direction = 0   #정지
        speed = 0
    elif input_key == 'o':
        direction += 0   #정지
        speed += 0

    if (speed>250) :
        speed = 250
    elif (speed < -250):
        speed = -250

    if(direction < -7):
        direction = -7
    elif (direction > 7):
        direction = 7

    return (direction, speed, brk)

def receive_from_Ard():     # Argument : ser ?
    ser.flushInput()
    ser.flushOutput()
    if ser.readable():
        res = ser.readline()
        res = res.decode()[:len(res)-1]     # "angle : 0 straight :0 Read/Map [A0]/[b]: 575 / 31"
        direction_cur = int(res[-3:])        # read b (= 31)
        #print('mapped_angle: ', direction_cur)
        #print('res: ', res)
    #print('------------------')

    return direction_cur


if __name__ == '__main__':

    
    path = '/home/skkcar/Desktop/contest/data_img/exception/'     ###

    try:
        if not os.path.exists(path):
            os.mkdir(path)    
    except OSError:
        print('Error: Creating dirctory. ' + path)

    # Variables
    ser = serial.Serial()
    ser.port = '/dev/ttyUSB0'      ### 아두이노 우노 (디버그용)
    # ser.port = '/dev/ttyACM0'       ### 아두이노 메가
    ser.baudrate = 9600

    message = 'a0s0'
    message_prev = 'a0s0'
    direction = 0
    speed = 0

    keys = ['w', 'a', 'd', 's', 'r', 'o', 'f', 'c']  # control keys ('o' : meaningless key)


    FPS = 15        ### FPS for Read
    FWPS = 3        ### FPS for Write
    is_FWPS = 0 

    image_width = 640
    image_height = 480


    cap_f = cv2.VideoCapture(2)    
    cap_f.set(cv2.CAP_PROP_BUFFERSIZE, 1)           
    cap_f.set(cv2.CAP_PROP_FRAME_WIDTH, image_width)      ### 864
    cap_f.set(cv2.CAP_PROP_FRAME_HEIGHT, image_height)     ### 480
   
    # cap_b = cv2.VideoCapture(4)     
    # cap_b.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    # cap_b.set(cv2.CAP_PROP_FRAME_WIDTH, image_width)      ### 864
    # cap_b.set(cv2.CAP_PROP_FRAME_HEIGHT, image_height)     ### 480

    print(cv2.__version__) 
    print(cap_f.isOpened())
    # print(cap_b.isOpened())

    # FPS 확인
    fps_f = cap_f.get(cv2.CAP_PROP_FPS)     
    print('fps front', fps_f)
    # fps_b = cap_b.get(cv2.CAP_PROP_FPS)     
    # print('fps back', fps_b)

    ser.open()
    time.sleep(2)

    time_prev_read = time.time()
    time_prev_write = time.time()

    while True:
        retval_f, img_f = cap_f.read()  # left cam
        # retval_b, img_b = cap_b.read()  # right cam
        time_pass_read = time.time() - time_prev_read
        time_pass_write = time.time() - time_prev_write
        input_key = 'o'

        # check whether one of the control keys is pressed
        for k in keys:
            if keyboard.is_pressed(k):
                input_key = k
        
        # Communicate with Arduino
        #if (retval_f is True):
        if (time_pass_read > 1./ FPS) :

            direction, speed, brk = dir_and_speed(input_key, direction, speed)
            if (brk == 1):
                break
            message = 'a' + str(direction) + 's' + str(speed)
            ser.write(message.encode())      
            print(message)
            time_prev_read  = time.time()


            # mapped_besistance from Arduino (rename to direction_cur)
            #direction_cur = receive_from_Ard()
            direction_cur = 0

            img_f_bird = total_function(img_f, 'front')     # image processed front
            #img_b_bird = total_function(img_b, 'back')     # image processed back
            preprocess_img = total(img_f_bird)
            binary_img = cvt_binary(img_f_bird)
            #cv2.imshow('Video_f', img_f)
            #cv2.imshow('Video_b', img_b)            
            cv2.imshow('Video_f_bird', img_f_bird)
            cv2.imshow('Video_f_preprocess', preprocess_img)
            cv2.imshow('Video_f_binary', binary_img)
            
            # print(img_p_f.shape)

        # Write(Store) Image
        
        
        if (   (  ((is_FWPS) and (time_pass_write > 1./FWPS))  or input_key == 'c' ) and direction_cur != -100):
            time_stamp = str(time.time())
            uuid_cur = str(uuid.uuid1())
            
            # img_f_title = "{0}f--{1}--{2}--{3}".format(path, str(message), time_stamp, uuid_cur)
            # cv2.imwrite(img_f_title+".png", img_f)
            
            #img_b_title = "{0}b--{1}--{2}--{3}".format(path, str(message), time_stamp, uuid_cur)
            # cv2.imwrite(path+img_b_title+".png", img_b)
            
        
            img_f_bird_title = "{0}f_bird--basic--{1}--{2}--{3}".format(path, str(message), time_stamp, uuid_cur)
            preprocess_img_title = "{0}f_bird--preprocess--{1}--{2}--{3}".format(path, str(message), time_stamp, uuid_cur)
            binary_img_title = "{0}f_bird--binary--{1}--{2}--{3}".format(path, str(message), time_stamp, uuid_cur)
            cv2.imwrite(img_f_bird_title + ".png", img_f_bird)
            cv2.imwrite(preprocess_img_title+ ".png", preprocess_img)
            cv2.imwrite(binary_img_title+ ".png", binary_img)
            
            time_prev_write = time.time()

        # Break Loop
        #time_s = time.time()
        if cv2.waitKey(10) == ord('f') :
            break
        #time_f = time.time()

        #print(time_f - time_s)


    ser.close()
    if cap_f.isOpened():
        cap_f.release()
    # if cap_b.isOpened():
        # cap_b.release()

    cv2.destroyAllWindows()

