import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QTextEdit, QComboBox, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QImage, QPixmap
import serial
from PyQt5.QtCore import QTimer
import pycuda.autoinit  # 自动初始化CUDA
import time
import serial.tools.list_ports
from mygpio import GPIOReader
from uart import *
import cv2
import time
import ctypes
from yolov7_inference import *
from stm32 import STM32CONTROL
from GUI import MYGUI
from image import *

class VideoPlayer(MYGUI,QWidget,STM32CONTROL):
    def __init__(self):
        super().__init__()

        self.gpio_reader = GPIOReader([35, 36, 37, 38, 40])
        self.update_serial_ports()
        self.connect_serial()
        self.play_button.clicked.connect(self.toggle_video)
        self.switch_button.clicked.connect(self.switch_source)
        self.connect_button.clicked.connect(self.connect_serial)
        self.clear_button.clicked.connect(self.clear_text_edit)
        self.action1_button.clicked.connect(self.action1)
        self.action2_button.clicked.connect(self.action2)
        self.action3_button.clicked.connect(self.action3)
        self.action4_button.clicked.connect(self.action4)
        self.Reset_button.clicked.connect(self.Reset)

        #yolo初始化部分
        ctypes.CDLL("libmyplugins.so")
        self.categories = ['Hazardous waste', 'Kitchen waste', 'Other waste', 'Recyclable waste']
        self.colors = [(0, 0, 255), (255, 0, 0), (244, 164, 96), (0, 255, 0)]
        self.yolov7_wrapper = YoLov7TRT("best_600.engine")

        self.infer_start_time = time.time()
        self.infer_result = None
        self.accumulated_category_count = {label: 0 for label in self.categories}

        self.camera_id = 0
        self.video_file = '1.mp4'
        self.cap = cv2.VideoCapture(self.video_file)

        self.is_playing = True #画面显示
        self.camera_is_playing = False #摄像头正在运行
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
        self.log_message("Initialized video player.")

        self.serial_timer = QTimer()#串口扫描
        self.serial_timer.timeout.connect(self.check_serial_status)
        self.serial_timer.start(1000)  # 1000 ms = 1 Hz

        self.gpio_timer = QTimer()#满载检测
        self.gpio_timer.timeout.connect(self.update_gpio_values)
        self.gpio_timer.start(1000)  # 1000 ms = 1 Hz

        self.Reset_timer = QTimer()#图像结果处理定时器
        self.Reset_timer_isOn = False
        self.Reset_timer.setSingleShot(True)  # 设置为一次性定时器
        self.Reset_timer.timeout.connect(self.Reset_Accumulated)

    def Reset_Accumulated(self):
        self.accumulated_category_count = {label: 0 for label in self.categories}
        self.Reset_timer_isOn = False

    def update_serial_ports(self):
        ports = self.scan_ports()
        self.port_combo.clear()
        for port in ports:
            self.port_combo.addItem(port)

    def connect_serial(self):
        try:
            if self.uart_running:
                self.uart_stop()
                self.connect_button.setText("连接串口")  # Change to "Connect Serial Port"
                self.log_message("Disconnected from serial port.")
            else:
                selected_port = self.port_combo.currentText()
                self.connect_to_port(selected_port)
                self.uart_start()
                self.connect_button.setText("断开串口")  # Change to "Disconnect Serial Port"
                self.log_message(f"Connected to serial port: {selected_port}")
        except Exception as e:
            self.log_message(f"Error: {str(e)}")  # Log the error message
            self.connect_button.setText("连接串口")  # Reset button text to "Connect Serial Port"
            self.log_message("Failed to connect/disconnect from serial port.")


    def check_serial_status(self):
        ports = self.scan_ports()
        self.port_combo.clear()
        for port in ports:
            self.port_combo.addItem(port)

    def display_uart_data(self, data):
        self.text_uart.append(data)

    def clear_text_edit(self):
        self.text_log.clear()

    def log_message(self, message):
        self.text_log.append(message)

    def update_gpio_values(self):
        gpio_values = self.gpio_reader.read_pin_states()  # 假设这个方法返回一个字典
        self.gpio_table.setItem(0, 0, QTableWidgetItem("满载" if gpio_values.get(35) else "未满载"))
        self.gpio_table.setItem(1, 0, QTableWidgetItem("满载" if gpio_values.get(36) else "未满载"))
        self.gpio_table.setItem(2, 0, QTableWidgetItem("满载" if gpio_values.get(37) else "未满载"))
        self.gpio_table.setItem(3, 0, QTableWidgetItem("满载" if gpio_values.get(38) else "未满载"))
        if not gpio_values.get(40):
            if self.camera_is_playing:
                pass
            else:
                if self.cap.isOpened():
                    self.cap.release()
                self.cap = cv2.VideoCapture(self.camera_id)
                self.log_message(f"Switched to camera: {self.camera_id}")
                self.camera_is_playing = True
        else:
            if self.camera_is_playing:
                if self.cap.isOpened():
                    self.cap.release()
                self.cap = cv2.VideoCapture(self.video_file)
                self.log_message(f"Switched to video: {self.video_file}")
                self.camera_is_playing = False
            else:
                pass

    def toggle_video(self):
        if not self.cap.isOpened():
            self.log_message("Error: 摄像头未打开")  # "Error: Camera not opened"
            return
        if self.is_playing:
            self.timer.stop()
            self.play_button.setText("开始")  # "Start"
            self.log_message("Paused playback.")
        else:
            if self.camera_is_playing:
                self.timer.start(1)
            else:
                self.timer.start(30)
            self.play_button.setText("暂停")  # "Pause"
            self.log_message("Started playback.")
        self.is_playing = not self.is_playing


    def switch_source(self):
        if self.cap.isOpened():
            self.cap.release()
        if self.camera_is_playing:
            self.camera_is_playing = not self.camera_is_playing
            self.cap = cv2.VideoCapture(self.video_file)
            self.log_message(f"Switched to video: {self.video_file}")
        else:
            self.camera_is_playing = not self.camera_is_playing
            self.cap = cv2.VideoCapture(self.camera_id)
            self.log_message(f"Switched to camera: {self.camera_id}")

    def accumulate_and_check_category_count(self, frame_category_count):
        for label, count in frame_category_count.items():
            self.accumulated_category_count[label] += count
        total_count = sum(self.accumulated_category_count.values())
        if total_count >= 10:
            most_frequent_category = max(self.accumulated_category_count, key=self.accumulated_category_count.get)
            self.accumulated_category_count.update({label: 0 for label in self.categories})
            most_frequent_index = self.categories.index(most_frequent_category)
            self.log_message(f"Most frequent category: {most_frequent_category} with count {self.accumulated_category_count[most_frequent_category]}")
            return most_frequent_index
        else:
            return None


    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.log_message("End of video reached. Restarting...")
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return
        if self.camera_is_playing:
                frame_with_boxes,category_count = self.detect_image(frame)#检测并返回图像结果和一个字典
                num = self.accumulate_and_check_category_count(category_count)
                if num is not None:
                    self.handle_action(num)
                self.log_message(f"Category counts: {self.accumulated_category_count}:{sum(self.accumulated_category_count.values())}")
                if(sum(self.accumulated_category_count.values())>0):
                    if self.is_running:
                        self.motor_stop()
                    if not self.Reset_timer_isOn:
                        self.Reset_timer_isOn = True
                        self.Reset_timer.start(4000)#5s内检测完
                else:
                    if not self.is_running:
                        self.take_out()
                        self.motor_start()
                self.SendImage2Lable(frame_with_boxes)
        else:
            self.SendImage2Lable(frame)

    def handle_action(self, num):
        # 创建一个字典，映射数字到对应的操作和日志
        actions = {
            0: ("action1", self.action1),
            1: ("action2", self.action2),
            2: ("action3", self.action3),
            3: ("action4", self.action4)
        }

        # 如果 num 存在于字典中，则执行相应的操作
        if num is not None and num in actions:
            action_name, action_func = actions[num]
            self.log_message(action_name)
            action_func()

    def detect_image(self,frame):
            result = compare_images3("background.jpg",frame)
            print(result["non_zero_count"])
            if(not result["result"]):
                input_image, _ = self.yolov7_wrapper.preprocess_image(frame)
                output = self.yolov7_wrapper.infer(input_image)
                result_boxes = self.yolov7_wrapper.post_process(output, frame.shape[0], frame.shape[1])
                # 记录推理结束时间
                infer_end_time = time.time()
                # 计算推理时间（毫秒）
                infer_time = infer_end_time - self.infer_start_time
                self.infer_start_time = infer_end_time
                fps = 1 / infer_time
                cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                return plot_boxes(frame, result_boxes, self.categories, self.colors)
            else:
                category_count = {label: 0 for label in self.categories}
                return frame, category_count

    def SendImage2Lable(self,frame):
        frame = cv2.resize(frame, self.video_size)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channels = frame.shape
        bytes_per_line = channels * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(q_image))

    def closeEvent(self, event):
        if self.cap.isOpened():
            self.cap.release()  # Release the video capture object
        self.uart_stop()  # Stop the serial thread
        event.accept()  # Accept the event to close the window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
