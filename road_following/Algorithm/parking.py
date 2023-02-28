import numpy as np
import time
import sys

def lidar_condition(scan, search_distance = None, min_angle1 = None, max_angle1 = None, min_angle2 = None, max_angle2 = None):
    if min_angle2 == None and max_angle2 == None:
        condition = (((min_angle1 < scan[:,0]) & (scan[:,0] < max_angle1)) &
                 (scan[:,1] < search_distance))
    else:
        condition = ((((min_angle1 < scan[:,0]) & (scan[:,0] < max_angle1)) | ((min_angle2 < scan[:,0]) & (scan[:,0] < max_angle2))) &
                    (scan[:,1] < search_distance))
    return condition

def detect_parking_car(lidar_module, c):
    try:
        scan = np.array(lidar_module.iter_scans())
        # print(scan)
        car_search_condition = lidar_condition(scan, 3000, -100, -90)
        print(scan[car_search_condition])
        c = detect_counting(car_search_condition, c)
        print(c.detect_cnt)
        if c.flag == True:
            print("Detect!")
            if c.obj == False:
                c.new_car_cnt += 1
            c.obj = True
        else:
            print("not detect!")
            c.obj = False

        return c
        
    except Exception as e:
        _, _, tb = sys.exc_info()
        print("car detect error = {}, error line = {}".format(e, tb.tb_lineno))

    
    
def stay_with_lidar(lidar_module, serial, speed, direction, rest_time = 1):
    start_time = time.time()
    end_time = time.time()
    while(end_time - start_time < rest_time):
        
        scan = np.array(lidar_module.iter_scans())
        message = "a" + str(direction) + "s" + str(speed)
        serial.write(message.encode())
        end_time = time.time()   

def near_detect_car(lidar_module, distance):
    scan = np.array(lidar_module.iter_scans())
    near_detect_condition = lidar_condition(scan, distance, -100, 100) # 625, 725, 800
    print(scan[np.where(near_detect_condition)])
    if len(np.where(near_detect_condition)[0]):
        return True
    else:
        return False
    
def escape(lidar_module):
    scan = np.array(lidar_module.iter_scans())
    escape_condition = lidar_condition(scan, 1200, -100, 100)
    
    if len(np.where(escape_condition)[0]) == 0:
        return True # 주변에 물체가 없으면 True 반환
    else:
        return False

def steering_parking(lidar_module, c, left_direction = 100):
    scan = np.array(lidar_module.iter_scans())
    detect_condition = lidar_condition(scan, 3000, -100, left_direction)
    detect_scan = scan[np.where(detect_condition)]
    steering_angle, distance_bias, c = parking_steering_angle(detect_scan, c)
    # print(steering_angle)
    f = lambda x : x**2 * (7/(600)**2) if x>0 else -1 * x**2 * (7/(600)**2)
    direction = return_parking_direction(-1 * steering_angle) + int(f(distance_bias))
    print("direction by gradient : ", return_parking_direction(-1 * steering_angle))
    print("direction by distance : ", int(f(distance_bias)))
    
    direction = 7 if direction >= 7 else direction
    direction = -7 if direction <= -7 else direction
    print(direction)
    return direction, c


def rest(serial, sleep_time):
    message = 'a0s0o0'
    serial.write(message.encode())
    time.sleep(sleep_time)
    return True

def parking_steering_angle(scan, c, mode = 'angle'):
    delta_threshold = 10
    
    queue_key_arr = (np.ones(len(scan))* c.queue_key).reshape(-1, 1)
    concat_scan = np.concatenate((queue_key_arr, scan), axis=1)

    if mode == 'angle':
        try:
            c.total_array = c.total_array[np.where(c.total_array[:,0] != c.queue_key)]
            c.total_array = np.concatenate((c.total_array, concat_scan), axis = 0)
            c.total_array = c.total_array[np.where(c.total_array[:,0] != -1)]
            
            theta = c.total_array[:,1]
            theta_idx = np.argsort(theta)
            c.total_array = c.total_array[theta_idx]

            next_tot = np.zeros(c.total_array.shape)
            next_tot[:len(theta)-1] = c.total_array[1:]
            next_tot[len(theta)-1] = c.total_array[0]
            delta_tot = np.abs((c.total_array - next_tot)[1:len(c.total_array) - 1])
            delta_angle = delta_tot[:,1]
            

            ret_idx = np.argmax(delta_angle)
            
            if delta_angle[ret_idx] < delta_threshold:
                pass
            
            if len(delta_angle) < 3:
                print("Delta error")
                return 0, 0, c
            # return
            print(c.total_array)
            print("steering angle : {}".format((c.total_array[ret_idx+1, 1] + c.total_array[ret_idx+2, 1])/2))
            distance_bias = c.total_array[ret_idx+1, 2] - c.total_array[ret_idx+2, 2]
            print("distance_bias : ", distance_bias)
            return (c.total_array[ret_idx+1, 1] + c.total_array[ret_idx+2, 1])/2, distance_bias,  c
        except Exception as e:
            _, _, tb = sys.exc_info()
            print("parking steering angle error = {}, error line = {}".format(e, tb.tb_lineno))
            
            return 0, 0, c
    if mode == 'distance':
        try:
            c.total_array = c.total_array[np.where(c.total_array[:,0] != c.queue_key)]
            c.total_array = np.concatenate((c.total_array, concat_scan), axis = 0)
            c.total_array = c.total_array[np.where(c.total_array[:,0] != -1)]
            ret_idx = np.argmin(c.total_array[:,2])


            if len(c.total_array) < 3:
                print("Too short array error")
                return 0, c
            # return
            return c.total_array[ret_idx][1], c
        except Exception as e:
            _, _, tb = sys.exc_info()
            print("parking steering distance error = {}, error line = {}".format(e, tb.tb_lineno))
            
            return None, c



def return_parking_direction(parking_gradient):
    f = lambda x :  7/20 * x
    ret_direction = int(f(parking_gradient))
    
    ret_direction = 7 if ret_direction >= 7 else ret_direction
    ret_direction = -7 if ret_direction <= -7 else ret_direction
    return ret_direction

def calculate_distance(lidar_module):

    try:
        total_left_scan = []
        total_right_scan = []
        for i in range(5):
            scan = np.array(lidar_module.iter_scans())

            right_condition = lidar_condition(scan, 2000, -100, -70)
            left_condition = lidar_condition(scan, 2000, 70, 100)

            left_scan = scan[np.where(left_condition)]
            right_scan = scan[np.where(right_condition)]
            
            if i == 0:
                total_left_scan = left_scan
                total_right_scan = right_scan
            else:
                total_left_scan = np.concatenate((total_left_scan, left_scan), axis = 0)
                total_right_scan = np.concatenate((total_right_scan, right_scan), axis = 0)   
        left_distance = np.min(total_left_scan[:,1])
        right_distance = np.min(total_right_scan[:,1])

        return left_distance, right_distance
    except Exception as e:
        _, _, tb = sys.exc_info()
        print("calculate distance error = {}, error line = {}".format(e, tb.tb_lineno))


def detailed_parking(lidar_module, c):
    scan = np.array(lidar_module.iter_scans())
    right_condition = lidar_condition(scan, 1000, -100, -30)
    left_condition = lidar_condition(scan, 1000, 30, 100)
    
    left_scan = scan[np.where(left_condition)]
    right_scan = scan[np.where(right_condition)]

    
    left_angle, c = parking_steering_angle(left_scan, c, 'distance')
    right_angle, c = parking_steering_angle(right_scan, c, 'distance')

    
    try: 
        if 80 <= left_angle and left_angle <= 100:
            direction = 0
        else:
            direction = int((80 - left_angle) * 7/30)
        
        if -100 <= right_angle and right_angle <= -80:
            direction = 0
        else:
            direction = int((-80 - right_angle) * 7/30)
    except Exception as e:
        _, _, tb = sys.exc_info()
        print("detailed parking error = {}, error line = {}".format(e, tb.tb_lineno))
        direction = 0
        c.stop = True

    return direction, c

def stop(lidar_module, c):
    scan = np.array(lidar_module.iter_scans())
    
    stop_condition = lidar_condition(scan, 1000, -80, -70, 70, 80)
    
    return detect_counting(stop_condition, c)

def search_left_right(lidar_module, c):
    scan = np.array(lidar_module.iter_scans())
    condition = lidar_condition(scan, 2000, -100, -70, 70, 100)
    return detect_counting(condition, c)
    
    
def escape_parking(lidar_module, c):
    scan = np.array(lidar_module.iter_scans())

    condition = lidar_condition(scan, 2000, -65, -55, 55, 65)
    return detect_counting(condition, c)

    
    
def detect_counting(condition1, c): # 3번 연속 detect 했을때 True return
    
    if len(np.where(condition1)[0]):
        if c.detect_cnt < 5:
            c.detect_cnt += 1
    else:
        if c.detect_cnt > 0:
            c.detect_cnt -= 1
        
    if c.detect_cnt == 5:
        c.flag = True
        return c
    elif c.detect_cnt == 0:
        c.flag = False
        return c
    else:
        return c

# def detect_counting2(condition1, condition2, c): # 3번 연속 detect 했을때 True return
    
#     if len(np.where(condition1)[0]) and len(np.where(condition2)[0]):
#         if c.detect_cnt < 5:
#             c.detect_cnt += 1
#     else:
#         if c.detect_cnt > 0:
#             c.detect_cnt -= 1
        
#     if c.detect_cnt == 5:
#         c.flag = True
#         return c
#     elif c.detect_cnt == 0:
#         c.flag = False
#         return c
#     else:
#         return c