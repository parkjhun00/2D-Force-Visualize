import numpy as np
import cv2
from cv2 import aruco

def calculate_yaw_diff(corners, marker_length, mtx, dist):
    yaw_diff = None

    if len(corners) >= 2:
        yaws = []

        for corner in corners[:2]:  # 最初の2つのマーカーのみを使用
            rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corner, marker_length, mtx, dist)

            # 不要なaxisを除去
            tvec = np.squeeze(tvec)
            rvec = np.squeeze(rvec)

            # 回転ベクトルからrodoriguesへ変換
            rvec_matrix = cv2.Rodrigues(rvec)
            rvec_matrix = rvec_matrix[0]

            # 並進ベクトルの転置
            transpose_tvec = tvec[np.newaxis, :].T

            # 合成
            proj_matrix = np.hstack((rvec_matrix, transpose_tvec))
            euler_angle = cv2.decomposeProjectionMatrix(proj_matrix)[6] # [deg]

            # x, y, z euler_angle値をfloatに変換
            #x = float(tvec[0])
            #y = float(tvec[1])
            #z = float(tvec[2])
            #roll = float(euler_angle[0])
            #pitch = float(euler_angle[1])
            #yaw = float(euler_angle[2])

            yaws.append(float(euler_angle[2]))  # ヨー角のみを追加

        yaw_diff = yaws[1] - yaws[0]

    if len(corners) < 2:
        yaw_diff = 99999

    return yaw_diff