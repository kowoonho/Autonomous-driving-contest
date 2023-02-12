import process
import sys
if __name__ == '__main__':
    play_name =sys.argv[1]
    if play_name == "Driving":
        driving_type = sys.argv[2] #  Time/Mission/parking_stage

        if len(sys.argv) == 4:
            speed_value = sys.argv[3]
        elif len(sys.argv) == 3:
            if sys.argv[2] == "Mission":
                speed_value = 150
            else:
                speed_value = 255
        processor = process.DoWork(play_name = "Driving", front_cam_name = "FRONT", rear_cam_name = "REAR", 
                                   rf_weight_file= "./model_weight_file/best_steering_model_0116.pth", 
                                   detect_weight_file="./model_weight_file/yolo_best_0205.pt",   # ./model_weight_file/yolo_final_weight.pt
                                   driving_type = driving_type, speed_value = speed_value)
        serial_result = processor.serial_start()
        if serial_result == True:
            front_camera_opened = processor.front_camera_start()
            if front_camera_opened == True:
                processor.Driving()

    elif play_name == "Parking":
        if len(sys.argv) == 2:
            parking_stage = 0
        else:
            parking_stage = sys.argv[2]

        if len(sys.argv) == 4:
            speed_value = sys.argv[3]
        else:
            speed_value = 80

        processor = process.DoWork(play_name = "Parking", front_cam_name = "FRONT", rear_cam_name = "REAR",
                                   detect_weight_file="./model_weight_file/yolo_final_weight.pt",
                                     parking_stage = parking_stage, speed_value = speed_value)
        serial_result = processor.serial_start()
        if serial_result == True:
            front_camera_opened = processor.front_camera_start()
            lidar_opened = processor.lidar_start()
            print("Lidar: ", lidar_opened)
            if front_camera_opened == True:
                processor.Parking()