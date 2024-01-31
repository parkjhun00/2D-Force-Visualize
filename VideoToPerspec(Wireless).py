from email.headerregistry import DateHeader
import os
import cv2
from cv2 import aruco
import numpy as np
import requests
from requests.auth import HTTPDigestAuth
import Equirec2Perspec as E2P 
from yaw_diff_calculation import calculate_yaw_diff


#接続設定
url = 'http://192.168.0.108/osc/commands/execute' #arp -a で IP確認して変更
username = "THETAYN35105632" #THETA + 下のシリアルナンバー
password = "35105632" #シリアルナンバーの数字だけ

payload = {
    "name": "camera.getLivePreview"
}

headers = {
    "Content-Type": "application/json;charset=utf-8"
}

response = requests.post(url, auth=HTTPDigestAuth(username, password), json=payload, headers=headers, stream=True)

# View設定
showWindow = 3

# ArUco マーカー設定
aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
aruco_params = aruco.DetectorParameters_create()
marker_length = 0.053  # [m]単位
mtx = np.load("mtx.npy")
dist = np.load("dist.npy")

if response.status_code == 200:
    bytes_ = bytes()
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            bytes_ += chunk
            a = bytes_.find(b'\xff\xd8')
            b = bytes_.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = bytes_[a:b+2]
                bytes_ = bytes_[b+2:]
                img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                if (showWindow == 1):

                    #平面への変換
                    equ = E2P.Equirectangular(img) 
                    #Specify parameters(FOV, theta, phi, height, width) THETA is left/right angle, PHI is up/down angle, both in degree
                    img = equ.GetPerspective(90, 180, -50, 500, 500) 

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

                    cv2.imshow("ArUco Mode", img)

                # ESC key will quit
                if cv2.waitKey(1) == 27:
                    break

else:
    print("Error: ", response.status_code)

cv2.destroyAllWindows()