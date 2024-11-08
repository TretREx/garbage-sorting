#用于拍背景
import cv2

# 初始化摄像头
cap = cv2.VideoCapture(0)

# 设置图像分辨率
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

frame_count = 0
background_saved = False

while frame_count < 10000:  # 循环直到捕获到第六帧
    ret, frame = cap.read()
    if not ret:
        print("未能捕获图像")
        break

    frame_count += 1

    if frame_count == 10:  # 第六帧时保存
        cv2.imwrite("background.jpg", frame)
        background_saved = True
        print("背景图片已保存为 background.jpg")
        break

# 释放摄像头
cap.release()

if not background_saved:
    print("未能保存背景图片")
