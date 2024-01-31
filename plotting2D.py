import os
import cv2
from cv2 import aruco
import numpy as np
import Equirec2Perspec as E2P
import pandas as pd
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
import socket
from collections import deque
import threading
from yaw_diff_calculation import calculate_yaw_diff

# センサーデータ取得関数
def get_sensor_data():
    global fz_values, fx_values
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 12345))
    server_socket.listen(1)

    while True:
        client_socket, address = server_socket.accept()
        data = client_socket.recv(1024)
        while data:
            data_values = data.decode('utf-8').split('\n')
            for value in data_values:
                if value:
                    fx_value_str, fz_value_str = value.split(',')
                    fx_values = float(fx_value_str.split(':')[1].strip())
                    fz_values = float(fz_value_str.split(':')[1].strip())
            data = client_socket.recv(1024)
        client_socket.close()

#PyQtGraph 画面更新
def update():
    global curve, fx_values, fz_values
    curve.setData([0, -fx_values], [0, -fz_values])
    curve.setPen(color=(255,255,255), width=8)

#回転
def rotate_point(x, y, angle_degrees):
    # 角度をラジアンに変換
    angle_radians = np.radians(angle_degrees)

    # 回転行列を定義
    rotation_matrix = np.array([
        [np.cos(angle_radians), -np.sin(angle_radians)],
        [np.sin(angle_radians), np.cos(angle_radians)]
    ])

    # 元の点
    original_point = np.array([x, y])

    # 回転後の点
    rotated_point = rotation_matrix.dot(original_point)

    return rotated_point

# グローバル変数
fz_values = 0
fx_values = 0
showWindow = 1 

# ArUco マーカー設定
aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
aruco_params = aruco.DetectorParameters_create()
marker_length = 0.053  # [m]単位
mtx = np.load("mtx.npy")
dist = np.load("dist.npy")

# ArUco マーカー設定
aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
aruco_params = aruco.DetectorParameters_create()
camera = cv2.VideoCapture(1)

# グラフ設定
app = pg.mkQApp("Plotting")
win = pg.GraphicsLayoutWidget(show=True, title="Basic plotting")
pg.setConfigOptions(antialias=True)
win.resize(1000,600)
win.setWindowTitle('Force Visualize')
p1 = win.addPlot(title="2D Visualize")
p1.setYRange(40, -40)
p1.setXRange(40, -40)
p1.showGrid(x=True, y=True)
curve = p1.plot()

# センサーデータ取得スレッド開始
data_thread = threading.Thread(target=get_sensor_data)
data_thread.start()

# メインループ
while True:
    ret, img = camera.read()
    if ret and showWindow:
        # 平面への変換
        equ = E2P.Equirectangular(img)
        img = equ.GetPerspective(90, 180, -50, 500, 500)

        # ArUco マーカー検出
        corners, ids, rejectedImgPoints = aruco.detectMarkers(img, aruco_dict, parameters=aruco_params)
        img = aruco.drawDetectedMarkers(img, corners, ids)

        yaw_diff = calculate_yaw_diff(corners, marker_length, mtx, dist)
        if yaw_diff is not None:
            print(f"Yaw Difference: {yaw_diff:.2f}")

        cv2.imshow("Panorama View", img)

    if yaw_diff == 99999:
        fz_values = 0
        fx_values = 0
    else:
        fz_values, fx_values = (fz_values, 0, yaw_diff)

    update()

    if cv2.waitKey(1) == 27:
        break

camera.release()
cv2.destroyAllWindows()
pg.exec()
