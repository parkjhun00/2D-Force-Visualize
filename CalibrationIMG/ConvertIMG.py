import os
import cv2
import Equirec2Perspec as E2P

def convert_and_save_image(file_path):
    # 이미지 파일을 변환하고 저장하는 함수
    equ = E2P.Equirectangular(file_path)  # Load equirectangular image

    # 변환 실행
    img = equ.GetPerspective(90, 180, -50, 1000, 1000)

    # 변환된 이미지 저장
    new_file_name = file_path.rsplit('.', 1)[0] + "_convert.jpg"
    cv2.imwrite(new_file_name, img)

# 현재 폴더의 모든 파일을 리스트로 가져옴
files = os.listdir('.')

# 이미지 파일만 골라내기 (jpg, jpeg, png)
image_files = [file for file in files if file.endswith(('.JPG', '.jpeg', '.png'))]

# 각 이미지 파일에 대하여 변환 및 저장 실행
for image_file in image_files:
    convert_and_save_image(image_file)
