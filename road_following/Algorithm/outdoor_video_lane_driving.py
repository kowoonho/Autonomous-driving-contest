import cv2
import time
from socket import *
import string
import os
import threading
from outdoor_lane_detection import *


# fixed global variable
image_height = 480
image_width = 640
toc = image_width * 0.55 # target of center( of lane)

#l = threading.Lock()

# Socket Generation
server = socket(AF_INET,SOCK_DGRAM)
server.setsockopt(SOL_SOCKET, SO_BROADCAST,1)


def driving_along_lane(dif, left_queue, right_queue):
    
    
    if (dif <= -25):
        # Ethernet_command('00110F')
        # print(time.time(), ': 우진')

        if ((right_queue & 0b11111)!=0b11111):
            ###Ethernet_command('00110F')
            print(time.time(), ': 우진')
            #print("right queue: ", end = '')
            #print('{:#b}'.format(right_queue))
        else:
            print(time.time(), ': 우진, 신호무시')

        left_queue = left_queue<<1
        right_queue = right_queue<<1
        right_queue = right_queue^1
    elif (dif >= 25):   # dif >= 10
        if ((left_queue & 0b11111)!=0b11111):
            ###Ethernet_command('00100F')
            print(time.time(), ': 좌진')
            #print("left queue: ", end = '')
            #print(left_queue&0b11111)
            #print(left_queue)
        else:
            print(time.time(), ': 좌진, 신호무시')
        left_queue = left_queue<<1
        right_queue = right_queue<<1
        left_queue = left_queue^1
    #left_queue<<1
    #right_queue<<1
    ###Ethernet_command('10000F')
    ###time.sleep(0.30)
    print(time.time(), ': 직진')
    ###Ethernet_command('00000F')
    ###time.sleep(0.15)
    
    return (left_queue,right_queue)

def Ethernet_command(direction):
    message_byte = bytes(direction, 'utf-8')
    server.sendto(message_byte,('192.168.10.255',8001))


def main():
    print(cv2.__version__)

    print(1)
    cap = cv2.VideoCapture('orange_line.mp4')
    #cap = cv2.VideoCapture(0)
    print(cap.isOpened())

    prev_frame_time = 0
    left_queue = 0b00000
    right_queue = 0b00000

    FPS = 15

    while(cap.isOpened()):   #VideoCapture의 성공 유/무를 반환

        ret, frame = cap.read()
        current_frame_time = time.time() - prev_frame_time

        if (ret is True) and (current_frame_time > 1./ FPS) :
            prev_frame_time = time.time()
            frame = cv2.resize(frame, (640, 480))
            
            col = center_of_lane(frame)
            dif = toc - col
            (left_queue, right_queue) = driving_along_lane(dif, left_queue, right_queue)
            #print("left : ", bin(left_queue))
            #print("right : ", bin(right_queue))
            frame_lane = lane_detect(frame)
            cv2.imshow('frame_lane', frame_lane)
            ###cv2.imshow('frame', frame)    ###

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()  #VideoCapture의 장치를 닫고 메모리를 해제
    print("release")
    cv2.destroyAllWindows()
    print("destory")


if __name__ == '__main__':
    main()
