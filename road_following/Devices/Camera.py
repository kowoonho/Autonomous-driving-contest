import cv2

class CameraModule():
    def __init__(self, width, height):
        self.image_width = width
        self.image_height = height
        
    
    def open_cam(self, cam_num):
        self.cam = cv2.VideoCapture(cam_num)
        self.cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)           
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.image_width)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.image_height)
        
    def read(self):
        if self.cam.isOpened():
            _, cam_img = self.cam.read()
            return cam_img
        else:
            return False, []
        
    def close_cam(self):
        if self.cam.isOpened():
            self.cam.release()
            return True
        else:
            return False
        