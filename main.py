import cv2
import numpy as np
import pycuda.autoinit  # 自动初始化CUDA
import pycuda.driver as cuda
import tensorrt as trt
import time
import ctypes

class YoLov7TRT:
    def __init__(self, engine_file_path, categories, default_conf_threshold=0.5, iou_threshold=0.4):
        """
        初始化YOLOv7 TensorRT推理器。

        :param engine_file_path: TensorRT引擎文件路径。
        :param categories: 类别名称列表。
        :param default_conf_threshold: 默认的置信度阈值（应用于所有类别）。
        :param iou_threshold: 非极大值抑制的IoU阈值。
        """
        self.categories = categories
        self.CONF_THRESH = {category: default_conf_threshold for category in categories}
        self.IOU_THRESHOLD = iou_threshold

        # 初始化CUDA上下文
        self.ctx = cuda.Device(0).make_context()
        self.stream = cuda.Stream()
        TRT_LOGGER = trt.Logger(trt.Logger.INFO)
        runtime = trt.Runtime(TRT_LOGGER)

        # 反序列化引擎文件
        with open(engine_file_path, "rb") as f:
            engine = runtime.deserialize_cuda_engine(f.read())
        self.context = engine.create_execution_context()

        # 初始化输入输出缓冲区
        self.host_inputs, self.cuda_inputs = [], []
        self.host_outputs, self.cuda_outputs = [], []
        self.bindings = []
        for binding in engine:
            size = trt.volume(engine.get_binding_shape(binding)) * engine.max_batch_size
            dtype = trt.nptype(engine.get_binding_dtype(binding))
            host_mem = cuda.pagelocked_empty(size, dtype)
            cuda_mem = cuda.mem_alloc(host_mem.nbytes)
            self.bindings.append(int(cuda_mem))
            if engine.binding_is_input(binding):
                self.input_w = engine.get_binding_shape(binding)[-1]
                self.input_h = engine.get_binding_shape(binding)[-2]
                self.host_inputs.append(host_mem)
                self.cuda_inputs.append(cuda_mem)
            else:
                self.host_outputs.append(host_mem)
                self.cuda_outputs.append(cuda_mem)

    def set_conf_threshold(self, category, threshold):
        """
        设置指定类别的置信度阈值。

        :param category: 类别名称。
        :param threshold: 置信度阈值（0到1之间）。
        """
        if category not in self.CONF_THRESH:
            raise ValueError(f"类别 '{category}' 不存在。")
        if not (0.0 <= threshold <= 1.0):
            raise ValueError("置信度阈值必须在0到1之间。")
        self.CONF_THRESH[category] = threshold

    def get_conf_threshold(self, category):
        """
        获取指定类别的置信度阈值。

        :param category: 类别名称。
        :return: 置信度阈值。
        """
        if category not in self.CONF_THRESH:
            raise ValueError(f"类别 '{category}' 不存在。")
        return self.CONF_THRESH[category]

    def infer(self, input_image):
        self.ctx.push()
        np.copyto(self.host_inputs[0], input_image.ravel())
        cuda.memcpy_htod_async(self.cuda_inputs[0], self.host_inputs[0], self.stream)
        self.context.execute_async(batch_size=1, bindings=self.bindings, stream_handle=self.stream.handle)
        cuda.memcpy_dtoh_async(self.host_outputs[0], self.cuda_outputs[0], self.stream)
        self.stream.synchronize()
        self.ctx.pop()
        return self.host_outputs[0]

    def preprocess_image(self, image):
        h, w, _ = image.shape
        r_w = self.input_w / w
        r_h = self.input_h / h
        if r_h > r_w:
            tw, th = self.input_w, int(r_w * h)
            tx1, ty1 = 0, int((self.input_h - th) / 2)
            tx2, ty2 = 0, self.input_h - th - ty1
        else:
            tw, th = int(r_h * w), self.input_h
            tx1, ty1 = int((self.input_w - tw) / 2), 0
            tx2, ty2 = self.input_w - tw - tx1, 0

        image = cv2.resize(image, (tw, th))
        image = cv2.copyMakeBorder(image, ty1, ty2, tx1, tx2, cv2.BORDER_CONSTANT, value=(128, 128, 128))
        image = np.transpose(image.astype(np.float32), [2, 0, 1]) / 255.0
        return np.ascontiguousarray(np.expand_dims(image, axis=0)), image

    def post_process(self, output, origin_h, origin_w):
        num = int(output[0])
        pred = np.reshape(output[1:], (-1, 6))[:num, :]

        if num == 0:
            return []

        # 获取类别索引
        class_indices = pred[:, 5].astype(int)
        # 获取类别名称
        class_names = [self.categories[idx] for idx in class_indices]
        # 获取对应的置信度阈值
        conf_thresholds = np.array([self.CONF_THRESH[name] for name in class_names], dtype=np.float32)
        # 根据每个框的类别对应的置信度阈值过滤
        boxes = pred[pred[:, 4] >= conf_thresholds]
        if len(boxes) == 0:
            return []

        boxes[:, :4] = self.xywh2xyxy(origin_h, origin_w, boxes[:, :4])

        confs = boxes[:, 4]
        boxes = boxes[np.argsort(-confs)]

        keep_boxes = []
        while boxes.shape[0]:
            current_box = boxes[0]
            keep_boxes.append(current_box)
            if boxes.shape[0] == 1:
                break
            ious = self.bbox_iou(np.expand_dims(current_box[:4], 0), boxes[1:, :4]).reshape(-1)
            label_matches = current_box[5] == boxes[1:, 5]
            invalid = (ious > self.IOU_THRESHOLD) & label_matches
            boxes = boxes[1:][~invalid]

        return np.stack(keep_boxes, 0) if len(keep_boxes) else np.array([])

    def xywh2xyxy(self, origin_h, origin_w, x):
        y = np.zeros_like(x)
        r_w = self.input_w / origin_w
        r_h = self.input_h / origin_h
        if r_h > r_w:
            y[:, 0] = x[:, 0] - x[:, 2] / 2
            y[:, 2] = x[:, 0] + x[:, 2] / 2
            y[:, 1] = x[:, 1] - x[:, 3] / 2 - (self.input_h - r_w * origin_h) / 2
            y[:, 3] = x[:, 1] + x[:, 3] / 2 - (self.input_h - r_w * origin_h) / 2
            y /= r_w
        else:
            y[:, 0] = x[:, 0] - x[:, 2] / 2 - (self.input_w - r_h * origin_w) / 2
            y[:, 2] = x[:, 0] + x[:, 2] / 2 - (self.input_w - r_h * origin_w) / 2
            y[:, 1] = x[:, 1] - x[:, 3] / 2
            y[:, 3] = x[:, 1] + x[:, 3] / 2
            y /= r_h
        return y

    def bbox_iou(self, box1, box2):
        b1_x1, b1_y1, b1_x2, b1_y2 = box1[:, 0], box1[:, 1], box1[:, 2], box1[:, 3]
        b2_x1, b2_y1, b2_x2, b2_y2 = box2[:, 0], box2[:, 1], box2[:, 2], box2[:, 3]

        inter_rect_x1 = np.maximum(b1_x1, b2_x1)
        inter_rect_y1 = np.maximum(b1_y1, b2_y1)
        inter_rect_x2 = np.minimum(b1_x2, b2_x2)
        inter_rect_y2 = np.minimum(b1_y2, b2_y2)

        inter_area = np.clip(inter_rect_x2 - inter_rect_x1 + 1, 0, None) * \
                     np.clip(inter_rect_y2 - inter_rect_y1 + 1, 0, None)

        b1_area = (b1_x2 - b1_x1 + 1) * (b1_y2 - b1_y1 + 1)
        b2_area = (b2_x2 - b2_x1 + 1) * (b2_y2 - b2_y1 + 1)

        return inter_area / (b1_area + b2_area - inter_area + 1e-16)

    def destroy(self):
        self.ctx.pop()

def plot_boxes(img, boxes, categories, colors):
    """
    在图像上绘制检测到的边界框。

    :param img: 原始图像。
    :param boxes: 检测到的边界框数组。
    :param categories: 类别名称列表。
    :param colors: 每个类别对应的颜色列表。
    :return: 绘制了边界框的图像和每个类别的计数字典。
    """
    # 初始化一个字典来计数每个类别
    category_count = {label: 0 for label in categories}

    for box in boxes:
        x1, y1, x2, y2 = map(int, box[:4])
        label_idx = int(box[5])
        label = categories[label_idx]
        color = colors[label_idx]

        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        cv2.putText(img, f"{label}:{box[4]:.2f}", (x1, y1 - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        if label in category_count:
            category_count[label] += 1
    return img, category_count

if __name__ == "__main__":
    engine_file_path = "yolov7-tiny.engine"
    ctypes.CDLL("libmyplugins.so")
    categories = ['Hazardous waste', 'Kitchen waste', 'Other waste', 'Recyclable waste']
    colors = [(0, 0, 255), (255, 0, 0), (244, 164, 96), (0, 255, 0)]

    # 初始化YOLOv7 TRT推理器
    yolov7_wrapper = YoLov7TRT(engine_file_path, categories=categories)

    # 设置每个类别的置信度阈值
    # 例如：'Hazardous waste': 0.6, 'Kitchen waste': 0.5, 'Other waste': 0.4, 'Recyclable waste': 0.7
    yolov7_wrapper.set_conf_threshold('Hazardous waste', 0.6)
    yolov7_wrapper.set_conf_threshold('Kitchen waste', 0.5)
    yolov7_wrapper.set_conf_threshold('Other waste', 0.4)
    yolov7_wrapper.set_conf_threshold('Recyclable waste', 0.7)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    try:
        frame_count = 0
        start_time = time.time()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            input_image, resized_image = yolov7_wrapper.preprocess_image(frame)
            # 记录推理开始时间
            infer_start_time = time.time()
            output = yolov7_wrapper.infer(input_image)
            result_boxes = yolov7_wrapper.post_process(output, frame.shape[0], frame.shape[1])
            # 记录推理结束时间
            infer_end_time = time.time()
            # 计算推理时间（毫秒）
            infer_time = (infer_end_time - infer_start_time) * 1000
            # 显示FPS
            elapsed_time = time.time() - start_time
            fps = frame_count / elapsed_time
            cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            frame_with_boxes, str_label = plot_boxes(frame, result_boxes, categories, colors)
            # 打印推理耗时
            print(f"Inference time: {infer_time:.2f} ms")
            cv2.imshow("YOLOv7 Inference", frame_with_boxes)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        yolov7_wrapper.destroy()
