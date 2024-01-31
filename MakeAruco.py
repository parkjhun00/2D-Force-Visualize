import cv2
from cv2 import aruco
import numpy as np

# ArUco マーカー選択
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

# マーカーID、サイズ指定
marker_id = 3 
marker_size = 200

# マーカー生成
marker_image = np.zeros((marker_size, marker_size), dtype=np.uint8)
marker_image = aruco.drawMarker(aruco_dict, marker_id, marker_size, marker_image, 1)

# マーカーセーブ＆表示
cv2.imwrite("aruco_marker_3.png", marker_image)
cv2.imshow('Marker', marker_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
