# 图片对比，检测是否有物体
import cv2
import numpy as np
import time
def compare_images(background_path, target_path, threshold=5000, kernel_size=(7, 7), blur_size=(5, 5), binary_thresh=30):
    background_img = cv2.imread(background_path, cv2.IMREAD_GRAYSCALE)
    target_img = cv2.imread(target_path, cv2.IMREAD_GRAYSCALE)
    if background_img is None or target_img is None:
        return None
    diff_img = cv2.absdiff(background_img, target_img)
    kernel = np.ones(kernel_size, np.uint8)
    open_img = cv2.morphologyEx(diff_img, cv2.MORPH_OPEN, kernel)
    blurred_img = cv2.GaussianBlur(open_img, blur_size, 0)
    _, binary_img = cv2.threshold(blurred_img, binary_thresh, 255, cv2.THRESH_BINARY)
    non_zero_count = cv2.countNonZero(binary_img)
    is_consistent = non_zero_count < threshold
    result = True if is_consistent else False
    return {
        "result": result,
        "non_zero_count":non_zero_count,
        "is_consistent": is_consistent,
        "binary_img": binary_img
    }

def compare_images2(background_img, target_img, threshold=5000, kernel_size=(7, 7), blur_size=(5, 5), binary_thresh=30):
    background_img = cv2.cvtColor(background_img, cv2.COLOR_BGR2GRAY)
    target_img = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)
    if background_img is None or target_img is None:
        return None
    diff_img = cv2.absdiff(background_img, target_img)
    kernel = np.ones(kernel_size, np.uint8)
    open_img = cv2.morphologyEx(diff_img, cv2.MORPH_OPEN, kernel)
    blurred_img = cv2.GaussianBlur(open_img, blur_size, 0)
    _, binary_img = cv2.threshold(blurred_img, binary_thresh, 255, cv2.THRESH_BINARY)
    non_zero_count = cv2.countNonZero(binary_img)
    is_consistent = non_zero_count < threshold
    result = is_consistent
    return {
        "result": result,
        "non_zero_count":non_zero_count,
        "is_consistent": is_consistent,
        "binary_img": binary_img
    }

def compare_images3(background_path,target_img , threshold=5000, kernel_size=(7, 7), blur_size=(5, 5), binary_thresh=30):
    background_img = cv2.imread(background_path)
    background_img = cv2.cvtColor(background_img, cv2.COLOR_BGR2GRAY)
    target_img = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)
    if background_img is None or target_img is None:
        return None
    diff_img = cv2.absdiff(background_img, target_img)
    kernel = np.ones(kernel_size, np.uint8)
    open_img = cv2.morphologyEx(diff_img, cv2.MORPH_OPEN, kernel)
    blurred_img = cv2.GaussianBlur(open_img, blur_size, 0)
    _, binary_img = cv2.threshold(blurred_img, binary_thresh, 255, cv2.THRESH_BINARY)
    non_zero_count = cv2.countNonZero(binary_img)
    is_consistent = non_zero_count < threshold
    result = True if is_consistent else False
    return result,binary_img
    # return {
    #     "result": result,
    #     "non_zero_count":non_zero_count,
    #     "is_consistent": is_consistent,
    #     "binary_img": binary_img
    # }

def Save_Background(img):
    cv2.imwrite("background.jpg", img)

if __name__ == "__main__":
    # result = compare_images('background.jpg', 'c1.jpg')
    # if result:
    #     print(result["non_zero_count"])
    #     print(result["result"])
    #     # cv2.imshow("Binary Image", result["binary_img"])
    #     # cv2.waitKey(0)
    #     cv2.destroyAllWindows()

    cap = cv2.VideoCapture(0)
    time.sleep(3)
    ret, background_img = cap.read()

    if not ret:
        print("Failed to capture background image")
        cap.release()
        cv2.destroyAllWindows()
    else:
        print("Background captured successfully")

    while True:
        # 读取当前帧
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            break

        # 使用 compare_images2 进行图像比较
        result = compare_images3("background.jpg", frame)

        # 显示结果
        print("Non-zero count:", result["non_zero_count"])
        print("Comparison result:", result["result"])

        # 显示二值化图像
        cv2.imshow("Binary Image", result["binary_img"])

        # 按 'q' 键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 释放摄像头和关闭窗口
    cap.release()
    cv2.destroyAllWindows()
