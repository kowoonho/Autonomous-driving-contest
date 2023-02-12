import cv2
import uuid
import os 

image_width = 640   # Hyper Para : (640,360)  (640,480)  (864,480)   
while True:
    cam_name = input("Enter Camera Name (f:Front, r:Rear) : ")
    if cam_name == 'f':
        cam_idx = 2
        image_height = 480 
        which_camera = 'front_'
        break
    elif cam_name == 'r':
        cam_idx = 4
        image_height = 360 
        which_camera = 'back_'
        break
    else:
        print("Wrong Camera")

# cap = cv2.VideoCapture('/dev/video2')
# cap = cv2.VideoCapture(2, cv2.CAP_V4L2)   # CAP_DSHOW : Microsoft, CAP_V4L2 : Linux
cap = cv2.VideoCapture(cam_idx)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, image_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, image_height)
print(cv2.__version__) 
print(cap.isOpened())

fps = cap.get(cv2.CAP_PROP_FPS)     # FPS 확인
print('fps', fps)

num_pic = int(input("찍을 사진 수 : "))
img_idx = 0

if num_pic == 0:        
    ret, frame = cap.read()
    while img_idx == num_pic:
        ret, frame = cap.read()
        
        if (ret is True):
            cv2.imshow('frame', frame)

            if cv2.waitKey(25) == ord('p') :
                print(frame.shape)
                path_cur = os.path.dirname(os.path.abspath(__file__))
                img_title = which_camera + 'img_for_srcmat'
                path_store = path_cur + "/data_img_srcmat/" + img_title + ".png"
                print(path_store)
                cv2.imwrite(path_store, frame)
                print('saved!')
                img_idx += 1
        
else:
    while img_idx < num_pic:
        ret, frame = cap.read()
        
        if (ret is True):
            # print(frame.shape)
            cv2.imshow('frame', frame)

            if cv2.waitKey(25) == ord('p') :
                path_cur = os.path.dirname(os.path.abspath(__file__))
                img_title = 'calib_before_' + str(uuid.uuid1())
                img_idx += 1
                cv2.imwrite(path_cur + img_title+".png", frame)
                print('saved {}!'.format(img_idx))
            
            # if cv2.waitKey(25) == ord('f') :
            #     break
        
cv2.destroyAllWindows()
cap.release() 
