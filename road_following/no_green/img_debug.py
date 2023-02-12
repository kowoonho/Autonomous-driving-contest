
import os
import cv2
from utility import dominant_gradient

path = './'

file_list = os.listdir(path)


if __name__ == '__main__':
    #print(file_list)
    for img_name in file_list:
        img = cv2.imread(path + img_name) 
        #edge_img = dominant_gradient(img)
        cv2.imshow('img', img)
        #cv2.imshow('edge_img', edge_img)
        cv2.waitKey()



'''
import cv2
import glob
import os
import sys
#rf_dir = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(rf_dir, "Algorithm"))
#rf_dir = os.path.dirname(os.path.abspath(__file__))

print(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(os.path.dirname((os.path.dirname(__file__))))
#print (rf_dir)
from Algorithm.img_process import color_filter 



if __name__ == "__main__":
    imgs = glob.glob("./*.png")
    for img in imgs:
        print(img)
        img = cv2.imread(img, 1)
        while True:
            #img_color = color_filter(img)


            cv2.imshow("img", img)
            #cv2.imshow("img_color", img_color)
            
            if cv2.waitKey(25) == ord('f'):
                cv2.destroyAllWindows()
                break




'''
