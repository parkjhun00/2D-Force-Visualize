import os
import cv2
from cv2 import aruco
import numpy as np
import Equirec2Perspec as E2P 
from yaw_diff_calculation import calculate_yaw_diff

# View設定 1 Normal 2 Panorama 3 Aruco
showWindow = 1 

# ArUco マーカー設定
aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
aruco_params = aruco.DetectorParameters_create()

camera = cv2.VideoCapture(1)                # カメラCh.指定

# ArUco マーカー設定
aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
aruco_params = aruco.DetectorParameters_create()
marker_length = 0.053  # [m]単位
mtx = np.load("mtx.npy")
dist = np.load("dist.npy")

while True:
    ret, img = camera.read()              # フレームを取得

    if (showWindow == 1):

        #平面への変換
        equ = E2P.Equirectangular(img) 
        #Specify parameters(FOV, theta, phi, height, width) THETA is left/right angle, PHI is up/down angle, both in degree
        img = equ.GetPerspective(90, 180, 0, 500, 500) 
                    
        # ArUco マーカー検出
        corners, ids, rejectedImgPoints = aruco.detectMarkers(img, aruco_dict, parameters=aruco_params)
        # ArUco マーカー表示
        img = aruco.drawDetectedMarkers(img, corners, ids)
        cv2.imshow("Normal View", img)

    if (showWindow == 2):
        cv2.imshow("Panorama View", img)

    if (showWindow == 3):

        #平面への変換
        equ = E2P.Equirectangular(img) 
        #Specify parameters(FOV, theta, phi, height, width) THETA is left/right angle, PHI is up/down angle, both in degree
        img = equ.GetPerspective(90, 180, -50, 500, 500) 

        # ArUco マーカー検出
        corners, ids, rejectedImgPoints = aruco.detectMarkers(img, aruco_dict, parameters=aruco_params)

        # ArUco マーカー表示
        img = aruco.drawDetectedMarkers(img, corners, ids)

        yaw_diff = calculate_yaw_diff(corners, marker_length, mtx, dist)

        if yaw_diff is not None:
            print(f"Yaw Difference: {yaw_diff:.2f}")

        cv2.imshow("Panorama View", img)

    # キー操作があればwhileループを抜ける
    if cv2.waitKey(1) == 27:
        break
 
# 撮影用オブジェクトとウィンドウの解放
camera.release()
cv2.destroyAllWindows()