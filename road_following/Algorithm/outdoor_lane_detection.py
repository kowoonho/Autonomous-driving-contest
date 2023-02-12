import cv2
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Global Variable
image_height = 480
image_width = 640



# BGR로 특정 색을 추출하는 함수 (흰색 라인 검출 용, 실내 : 검정)
def bgrExtraction(image):
    bgrLower = np.array([155, 175, 185])    # 추출할 색의 하한
    bgrUpper = np.array([255, 255, 255])    # 추출할 색의 상한
    img_mask = cv2.inRange(image, bgrLower, bgrUpper) 
    result = cv2.bitwise_and(image, image, mask=img_mask)
    ###cv2.imshow('bgr', result)
    return result


# HSV로 특정 색을 추출하는 함수 (노란색 라인 검출 용)
def hsvExtraction(image):
    hsvLower = np.array([10, 115, 180])    # 추출할 색의 하한
    hsvUpper = np.array([50, 225, 255])    # 추출할 색의 상한
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv_mask = cv2.inRange(hsv, hsvLower, hsvUpper) 
    result = cv2.bitwise_and(image, image, mask=hsv_mask)
    ###cv2.imshow('hsv', result)
    return result


def reg_of_interest(image) :    # Region of Interest(관심영역)
    image_height = image.shape[0]
    image_width = image.shape[1]
    
    polygons = np.array(    ### hyper parameter ###
        [[ (round(image_width * 0.00), image_height), \
            (round(image_width * 0.99), image_height), \
            (round(image_width * 0.99), round(image_height * 0.00)),\
            (round(image_width * 0.00), round(image_height * 0.00)) ]] )
    '''
    polygons = np.array([
    [   (round(image_width * 0.05), image_height),
        (round(image_width * 0.20), image_height),
        (round(image_width * 0.45), round(image_height * 0.70)),
        (round(image_width * 0.35), round(image_height * 0.70)) ] , 
    [   (round(image_width * 0.80), image_height),
        (round(image_width * 0.95), image_height),
        (round(image_width * 0.65), round(image_height * 0.70)),
        (round(image_width * 0.55), round(image_height * 0.70)) ]
    ])
    '''
    image_mask = np.zeros_like(image)
    cv2.fillPoly(image_mask, polygons, 255)
    masking_image = cv2.bitwise_and(image, image_mask)
    cv2.imshow('roi', masking_image)
    return masking_image

# 케니에지 처리하는 함수
def canny_edge(image) :
    gray_conversion = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ###cv2.imshow('gray', gray_conversion)
    blur_conversion = cv2.GaussianBlur(gray_conversion, (5, 5), 0)      ### hyper parameter ###
    ###cv2.imshow('blur', blur_conversion)
    canny_conversion = cv2.Canny(gray_conversion, 100, 100)              ### hyper parameter (hsv : 200, 200) ###
    ###cv2.imshow('canny', canny_conversion)
    return canny_conversion

def show_lines(image, lines) : 
    lines_image = np.zeros_like(image)
    if lines is not None :
        for i in range(len(lines)):
            for x1,y1,x2,y2 in lines[i]:
                if (x1 < (-10 * image_width)) or (x1 > 10 * image_width) :
                    lines_image = 0
                else:
                    cv2.line(lines_image,(x1,y1),(x2,y2),(255,0,0), 10 )
    return lines_image

# 여러 선을, 하나의 선으로 만들어 주는 함수.
# 방법은? 기울기와 y절편을 평균으로 해서 하나의 기울기와 y절편을 갖도록 만드는 방법.
def make_coordinates(image, line_parameters):
    if type(line_parameters) != np.float64:
        slope, intercept = line_parameters
        y1 = image.shape[0]
        y2 = int(y1*(3/5))
        x1 = int((y1- intercept)/slope)
        x2 = int((y2 - intercept)/slope) 
        return np.array([x1, y1, x2, y2])

def average_slope_intercept(image, lines):
    left_fit = []
    right_fit = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            try:
                parameter = np.polyfit((x1, x2), (y1, y2), 1)
            except:
                return None
            slope = parameter[0]
            
            #if (-0.5 < slope) and (slope < 0.5):
            #    continue
            #elif (slope > 2) or (slope < -2):
            #    continue
            if(1):
            #else:
                intercept = parameter[1]
                if slope < 0:
                    #if x1 > image_width * 0.6:
                    #    continue
                    left_fit.append((slope, intercept))
                else:
                    #if x2 < image_width * 0.4:
                    #    continue
                    right_fit.append((slope, intercept))

        left_fit_average =np.average(left_fit, axis=0)
        right_fit_average = np.average(right_fit, axis =0)
        left_line =make_coordinates(image, left_fit_average)
        right_line = make_coordinates(image, right_fit_average)

        if (left_line is None) and (right_line is None):
            return None
        elif (left_line is None):
            return np.array([[right_line]])
        elif (right_line is None):
            return np.array([[left_line]])
        else:
            return np.array([[left_line, right_line]])


def lane_detect(lanelines_image):
    bgr_extraction_image = bgrExtraction(lanelines_image)
    hsv_extraction_image = hsvExtraction(lanelines_image)
    extraction_image = cv2.add(bgr_extraction_image, hsv_extraction_image)
    
    #흰 검으로 변환해서 라인 검출함.
    canny_conversion = canny_edge(extraction_image)
    roi_conversion = reg_of_interest(canny_conversion)

    #라인 이어주기
    lines = cv2.HoughLinesP(roi_conversion, 2, np.pi/180., 50, minLineLength = 80, maxLineGap = 5)  ### hyper parameter ###

    #선을 기울기 평균값으로 적용
    averaged_lines = average_slope_intercept(lanelines_image, lines)
    #print(averaged_lines)
    lines_image = show_lines(lanelines_image, averaged_lines)
    ###lines_image = show_lines(lanelines_image, lines)

    #원본 이미지에 라인 그리기
    combine_image = cv2.addWeighted(lanelines_image, 0.8, lines_image, 1, 1)
    
    return combine_image
     
def center_of_lane(lanelines_image):
    bgr_extraction_image = bgrExtraction(lanelines_image)
    hsv_extraction_image = hsvExtraction(lanelines_image)
    extraction_image = cv2.add(bgr_extraction_image, hsv_extraction_image)
    ###cv2.imshow('extraction', extraction_image)
    
    #흰 검으로 변환해서 라인 검출함.
    canny_conversion = canny_edge(extraction_image)
    roi_conversion = reg_of_interest(canny_conversion)

    #라인 이어주기
    lines = cv2.HoughLinesP(roi_conversion, 2, np.pi/180., 50, minLineLength = 80, maxLineGap = 5)  ### hyper parameter ###

    #선을 기울기 평균값으로 적용
    averaged_lines = average_slope_intercept(lanelines_image, lines)
    ###print(averaged_lines)

    if (type(averaged_lines) == type(None)):
        center = image_width * 0.55
    else:
        if len(averaged_lines[0]) == 2:
            center = (averaged_lines[0, 0, 2] + averaged_lines[0, 1, 2]) / 2
        elif len(averaged_lines[0]) == 1:
            if averaged_lines[0, 0, 0] < averaged_lines[0, 0, 2]:
                center = averaged_lines[0, 0, 2]
                
            else:
                center = averaged_lines[0, 0, 2]
                print(averaged_lines)
    
    return center 

