import cv2
import numpy as np

def compare_images(background_path, target_path, threshold=50, kernel_size=(7, 7), blur_size=(5, 5), binary_thresh=30):
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

if __name__ == "__main__":
    result = compare_images('background.jpg', 'images/c1.jpg')
    if result:
        print(result["non_zero_count"])
        print(result["result"])
        cv2.imshow("Binary Image", result["binary_img"])
        cv2.waitKey(0)
        cv2.destroyAllWindows()
