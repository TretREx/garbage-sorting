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

class VideoPlayer(QWidget,STM32CONTROL):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("垃圾分类实验")  # "Garbage Classification Experiment"
        self.setFixedSize(1024, 600)

        self.gpio_reader = GPIOReader([35, 36, 37, 38, 40])

        # 创建一个表格来显示垃圾状态
        self.gpio_table = QTableWidget(self)
        self.gpio_table.setStyleSheet("font-size: 10pt;")  # Set font size for UART text box
        self.gpio_table.setFixedSize(300, 160)
        self.gpio_table.setGeometry(700, 400, 300, 160)  # 调整位置和大小
        self.gpio_table.setRowCount(4)  # 行数为 4（四种垃圾）
        self.gpio_table.setColumnCount(1)  # 列数为 1
        self.gpio_table.setHorizontalHeaderLabels(["垃圾状态"])  # 设置表头
        self.gpio_table.setVerticalHeaderLabels([
            "可回收垃圾",
            "厨余垃圾",
            "有害垃圾",
            "其他垃圾"
        ])  # 设置垂直表头

        self.video_label = QLabel(self)
        self.video_size = (640, 480)
        self.video_label.setFixedSize(self.video_size[0], self.video_size[1])
        self.video_label.setGeometry(20, 20, self.video_size[0], self.video_size[1])

        self.play_button = QPushButton("开始", self)  # "Start" in Chinese
        self.play_button.setFixedSize(50, 30)
        self.play_button.setGeometry(20, self.video_size[1] + 20, 50, 30)
        self.play_button.clicked.connect(self.toggle_video)

        self.switch_button = QPushButton("切换", self)  # "Switch" in Chinese
        self.switch_button.setFixedSize(50, 30)
        self.switch_button.setGeometry(self.video_size[0] + 20 - 50, self.video_size[1] + 20, 50, 30)
        self.switch_button.clicked.connect(self.switch_source)

        self.text_uart = QTextEdit("", self)
        self.text_uart.setReadOnly(True)
        self.text_uart.setStyleSheet("font-size: 10pt;")  # Set font size for UART text box
        self.text_uart.setFixedSize(300, 240)
        self.text_uart.setGeometry(700, 50, 300, 240)

        # Create a dropdown for serial port selection
        self.port_combo = QComboBox(self)
        self.port_combo.setGeometry(700, 10, 120, 30)
        self.update_serial_ports()

        # Create connect button
        self.connect_button = QPushButton("连接串口", self)  # "Connect Serial Port"
        self.connect_button.setGeometry(880, 10, 120, 30)
        self.connect_button.clicked.connect(self.connect_serial)

        self.text_log = QTextEdit("Log", self)
        self.text_log.setReadOnly(True)
        self.text_log.setStyleSheet("font-size: 10pt;")    # Set font size for log text box
        self.text_log.setFixedSize(640, 60)
        self.text_log.setGeometry(20, 540, 640, 60)

        self.clear_button = QPushButton('Clear Text', self)  # "Clear Text" in Chinese
        self.clear_button.setFixedSize(100, 30)
        self.clear_button.setGeometry(300, 500, 100, 30)
        self.clear_button.clicked.connect(self.clear_text_edit)


        self.is_running = False
        self.action1_button = QPushButton("Action1", self)  # "Start" in Chinese
        self.action1_button.setFixedSize(75, 30)
        self.action1_button.setGeometry(700, 310 , 75, 30)
        self.action1_button.clicked.connect(self.action1)

        self.action2_button = QPushButton("Action2", self)  # "Start" in Chinese
        self.action2_button.setFixedSize(75, 30)
        self.action2_button.setGeometry(780, 310 , 75, 30)
        self.action2_button.clicked.connect(self.action2)

        self.action3_button = QPushButton("Action3", self)  # "Start" in Chinese
        self.action3_button.setFixedSize(75, 30)
        self.action3_button.setGeometry(700, 350 , 75, 30)
        self.action3_button.clicked.connect(self.action3)

        self.action4_button = QPushButton("Action4", self)  # "Start" in Chinese
        self.action4_button.setFixedSize(75, 30)
        self.action4_button.setGeometry(780, 350 , 75, 30)
        self.action4_button.clicked.connect(self.action4)

        self.Reset_button = QPushButton("Reset", self)  # "Start" in Chinese
        self.Reset_button.setFixedSize(75, 30)
        self.Reset_button.setGeometry(860, 320 , 75, 30)
        self.Reset_button.clicked.connect(self.Reset)

        self.connect_serial()

        #yolo初始化部分
        ctypes.CDLL("libmyplugins.so")
        self.categories = ['Hazardous waste', 'Kitchen waste', 'Other waste', 'Recyclable waste']
        self.colors = [(0, 0, 255), (255, 0, 0), (244, 164, 96), (0, 255, 0)]
        self.yolov7_wrapper = YoLov7TRT("best_600.engine")
        # 记录推理开始时间
        self.infer_start_time = time.time()
        ###


        self.infer_result = None
        self.accumulated_category_count = {label: 0 for label in self.categories}

        self.Servo_Angle = 0
        self.Servo_Target_Angle = 0
        self.camera_id = 0
        self.video_file = '1.mp4'
        self.cap = cv2.VideoCapture(self.video_file)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.is_playing = True
        self.timer.start(30)
        self.camera_is_playing = False
        self.log_message("Initialized video player.")

        # Create a timer to check serial port status every second
        self.serial_timer = QTimer()
        self.serial_timer.timeout.connect(self.check_serial_status)
        self.serial_timer.start(1000)  # 1000 ms = 1 Hz

        # Create a timer to update GPIO values every second
        self.gpio_timer = QTimer()
        self.gpio_timer.timeout.connect(self.update_gpio_values)
        self.gpio_timer.start(1000)  # 1000 ms = 1 Hz

        self.Reset_timer = QTimer()
        self.Reset_timer_isOn = False
        self.Reset_timer.setSingleShot(True)  # 设置为一次性定时器
        self.Reset_timer.timeout.connect(self.Reset_Accumulated)

    def Reset_Accumulated(self):
        self.accumulated_category_count = {label: 0 for label in self.categories}
        self.Reset_timer_isOn = False

    def update_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        self.port_combo.clear()
        for port in ports:
            self.port_combo.addItem(port.device)

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
        self.gpio_table.setRowHeight(0, 35)
        self.gpio_table.setRowHeight(1, 35)
        self.gpio_table.setRowHeight(2, 35)
        self.gpio_table.setRowHeight(3, 35)
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
                frame_with_boxes,category_count = plot_boxes(frame, result_boxes, self.categories, self.colors)#画框加返回字典
                num = self.accumulate_and_check_category_count(category_count)
                if num != None:
                    if num == 0:
                        self.log_message("action1")
                        self.action1()
                    elif num == 1:
                        self.log_message("action2")
                        self.action2()
                    elif num == 2:
                        self.log_message("action3")
                        self.action3()
                    elif num == 3:
                        self.log_message("action4")
                        self.action4()
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
                frame = cv2.resize(frame_with_boxes, self.video_size)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channels = frame.shape
                bytes_per_line = channels * width
                q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
                self.video_label.setPixmap(QPixmap.fromImage(q_image))

        else:
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
