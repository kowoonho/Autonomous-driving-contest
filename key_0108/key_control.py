from socket import *
import string
import keyboard
import time
import serial

#server = socket(AF_INET,SOCK_DGRAM)
#server.setsockopt(SOL_SOCKET, SO_BROADCAST,1)

#direction = '00000F'
#message_byte = bytes(direction, 'utf-8')
#server.sendto(message_byte,('192.168.10.255',8001))

ser = serial.Serial()
ser.port = '/dev/ttyUSB0'
#ser.port = '/dev/ttyACM0'
ser.baudrate = 9600
ser.open()
time.sleep(2)


message = '0 0 '
message_prev = '0 0 '
direction = 0
speed = 0

keys = ['w', 'a', 'd', 's', 'r', 'o', 'f']
time_prev = time.time()
FPS = 20

while True:
    time_pass = time.time() - time_prev
    input_key = 'o'

    for k in keys:
        if keyboard.is_pressed(k):
            input_key = k

    if (time_pass > 1./ FPS) :
        if input_key == 'f':
            directon = 0
            speed = 0
            print('program finish')
            break
        elif input_key == 'w':#직진
            print('you pressed w')
            speed += 50
        elif input_key == 'a':#좌진
            print('you pressed a')
            direction -= 5
        elif input_key == 'd':#우진
            print('you pressed d')
            direction += 5 
        #elif input_key == 'q':#좌직진
        #    print('you pressed q')
        #    direction = -10
        #    speed = 150
        #elif input_key == 'e':#우직진
        #    print('you pressed e')
        #    direction = 10
        #    speed = 150
        #elif input_key == 'z':#좌후진
        #    print('you pressed z')
        #    direction = '11100F'
        #elif input_key == 'c':#우후진
        #    print('you pressed c')
        #    direction = '11110F'
        elif input_key == 's':#후진
            print('you pressed s')
            speed -= 50
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
        if(direction < -15):
            direction = -15
        elif (direction > 15):
            direction = 15
            
        message = str(direction) +  ' ' + str(speed) + ' '
        ser.write(message.encode())      
        print(message)
        # if message != message_prev:
        #     print(message)
        #     message_prev = message
        time_prev  = time.time()




