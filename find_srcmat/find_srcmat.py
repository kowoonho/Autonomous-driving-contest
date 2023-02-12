import cv2
import numpy as np
import pickle
import os


win_name = "scanning"
path_cur = os.path.dirname(os.path.abspath(__file__))
cam_name = input("Enter Camera Name (f:Front, r:Rear) : ")
image_width = 640
if cam_name == 'f':
    img_fullpath = path_cur + "/data_img_srcmat/front_img_for_srcmat.png"
    pkl_fullpath = path_cur + "/front_perspect_param.pkl"
    image_height = 480
elif cam_name == 'r':
    img_fullpath = path_cur + "/data_img_srcmat/back_img_for_srcmat.png"
    pkl_fullpath = path_cur + "/back_perspect_param.pkl"
    image_height = 360

img = cv2.imread(img_fullpath)
img = cv2.resize(img, (image_width, image_height))
rows, cols = img.shape[:2]
draw = img.copy()
pts_cnt = 0
pts = np.zeros((4, 2), dtype=np.float32)

def onMouse(event, x, y, flags, param):
    global pts_cnt
    if event == cv2.EVENT_LBUTTONDOWN:
        # 좌표에 초록색 동그라미 표시
        cv2.circle(draw, (x, y), 10, (0, 255, 0), -1)
        cv2.imshow(win_name, draw)

        # 마우스 좌표 저장
        pts[pts_cnt] = [x, y]
        print(pts[pts_cnt])
        pts_cnt += 1
        if pts_cnt == 4:
            # 좌표 4개 중 상하좌우 찾기
            sortedPts = pts[pts[:,1].argsort()]
            sortedPtsTop = sortedPts[0:2]
            sortedPtsBottom = sortedPts[2:4]
            topLeft = sortedPtsTop[np.argmin(sortedPtsTop[:, 0])]           # x+y가 가장 값이 좌상단 좌표
            topRight = sortedPtsTop[np.argmax(sortedPtsBottom[:, 0])]    # x-y가 가장 작은 것이 우상단 좌표
            bottomRight = sortedPtsBottom[np.argmax(sortedPtsTop[:, 0])]       # x+y가 가장 큰 값이 우하단 좌표
            bottomLeft = sortedPtsBottom[np.argmin(sortedPtsBottom[:, 0])]  # x-y가 가장 큰 값이 좌하단 좌표

            # 변환 전 4개 좌표 
            pts1 = np.float32([topLeft, topRight, bottomRight, bottomLeft])

            # 변환 후 영상에 사용할 서류의 폭과 높이 계산
            w1 = abs(bottomRight[0] - bottomLeft[0])
            w2 = abs(topRight[0] - topLeft[0])
            h1 = abs(topRight[1] - bottomRight[1])
            h2 = abs(topLeft[1] - bottomLeft[1])
            width = max([w1, w2])  # 두 좌우 거리간의 최대값이 서류의 폭
            height = max([h1, h2])  # 두 상하 거리간의 최대값이 서류의 높이

            # 변환 후 4개 좌표
            pts2 = np.float32([[200, 0], [400, 0],
                               [400, 300], [200, 300]])

            # 변환 행렬 계산 
            print(pts1)
            dic_param = {'pts_src': pts1}
            global pkl_fullpath
            with open(pkl_fullpath, 'wb') as f:
                pickle.dump(dic_param, f)
            mtrx = cv2.getPerspectiveTransform(pts1, pts2)
            # 원근 변환 적용
            result = cv2.warpPerspective(img, mtrx, (600, 300))
            cv2.imshow('scanned', result)
            cv2.imwrite(path_cur + '/warp.png', result)

cv2.imshow(win_name, img)
cv2.setMouseCallback(win_name, onMouse)
cv2.waitKey(0)
cv2.destroyAllWindows()


