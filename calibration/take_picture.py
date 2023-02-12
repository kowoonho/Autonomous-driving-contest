import cv2
import uuid
import os 


image_width = 640   # 640   864   
image_height = 360  # 480   480

# cap = cv2.VideoCapture('/dev/video2')
# cap = cv2.VideoCapture(2, cv2.CAP_V4L2)   # CAP_DSHOW : Microsoft, CAP_V4L2 : Linux
cap = cv2.VideoCapture(2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, image_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, image_height)
print(cv2.__version__) 
print(cap.isOpened())

fps = cap.get(cv2.CAP_PROP_FPS)     # FPS 확인
print('fps', fps)

num_pic = int(input("찍을 사진 수 : "))
img_idx = 0

if num_pic == 0:
    FB = input('Front of Back Camera ? (\'f\' or \'b\')')
    if FB == 'f':
        which_camera = 'front_'
    elif FB == 'b':
        which_camera = 'back_'
        
    ret, frame = cap.read()
    while img_idx == num_pic:
        ret, frame = cap.read()
        
        if (ret is True):
            # print(frame.shape)
            cv2.imshow('frame', frame)

            if cv2.waitKey(25) == ord('p') :
                path_cur = os.path.dirname(os.path.abspath(__file__))
                path = path_cur + '/data_img_srcmat/'
                img_title = which_camera + 'img_for_srcmat'
                img_idx += 1
                cv2.imwrite(path+img_title+".png", frame)
                print('saved!')
        
else:
    while img_idx < num_pic:
        ret, frame = cap.read()
        
        if (ret is True):
            # print(frame.shape)
            cv2.imshow('frame', frame)

            if cv2.waitKey(25) == ord('p') :
                path_cur = os.path.dirname(os.path.abspath(__file__))
                path = path_cur + '/data_img_calib/'
                img_title = 'calib_before_' + str(uuid.uuid1())
                img_idx += 1
                cv2.imwrite(path+img_title+".png", frame)
                print('saved {}!'.format(img_idx))
            
            # if cv2.waitKey(25) == ord('f') :
            #     break
        
