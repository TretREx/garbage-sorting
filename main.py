#主程序
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
from cap import Save_Background

class VideoPlayer(MYGUI,QWidget,STM32CONTROL):
    data_received = pyqtSignal(str)
    def __init__(self):
        super().__init__()

        self.last2states =0
        self.laststates=0
        self.categories_num = 0
        self.gpios = [21, 22, 23, 24, 26]
        self.gpio_reader = GPIOReader(self.gpios)

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
        self.Save_button.clicked.connect(self.SaveBackground)
        self.data_received.connect(self.update_uart_output)
        self.Start.clicked.connect(self.StartRun)

        #yolo初始化部分
        ctypes.CDLL("libmyplugins.so")
        self.categories = ['Hazardous waste', 'Kitchen waste', 'Other waste', 'Recyclable waste']
        self.colors = [(0, 0, 255), (255, 0, 0), (244, 164, 96), (0, 255, 0)]
        self.yolov7_wrapper = YoLov7TRT("yolov7-tiny.engine")

        self.infer_start_time = time.time()
        self.infer_result = None
        self.accumulated_category_count = {label: 0 for label in self.categories}

        # 打开摄像头
        self.camera_id = self.get_camera_id()
        if(self.camera_id == None):
            print("没有摄像头")
        else:
            print("")
        self.video_file = '1.mp4'
        self.cap = cv2.VideoCapture(self.video_file)

        self.is_playing = True #画面显示
        self.camera_is_playing = False #摄像头正在运行

        #图像更新
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
        self.log_message("Initialized video player.")

        self.serial_timer = QTimer()#串口扫描
        self.serial_timer.timeout.connect(self.update_serial_ports)
        self.serial_timer.start(1000)  # 1000 ms = 1 Hz

        self.serial_print_timer = QTimer(self)  # 创建定时器
        self.serial_print_timer.timeout.connect(self.check_serial_data)  # 设置定时器回调函数
        self.serial_print_timer.start(100)  # 每100毫秒（0.1秒）检查一次串口数据

        self.gpio_timer = QTimer()#满载检测
        self.gpio_timer.timeout.connect(self.update_gpio_values)
        self.gpio_timer.start(1000)  # 1000 ms = 1 Hz

        self.Reset_timer = QTimer()#图像结果处理定时器
        self.Reset_timer_isOn = False
        self.Reset_timer.setSingleShot(True)  # 设置为一次性定时器
        self.Reset_timer.timeout.connect(self.Reset_Accumulated)

    def check_serial_data(self):
        """定时检查串口数据并打印到终端"""
        try:
            if self.serial_port and self.serial_port.in_waiting > 0:
                data = self.serial_port.readline().decode('utf-8').strip()  # 读取数据
                if data:
                    print(f"收到数据: {data}")  # 打印到终端，中文支持
                    self.data_received.emit(data)  # 触发信号（如果需要的话）
        except serial.SerialException as e:
            # 捕获串口相关错误
            print(f"串口错误: {e}")
        except UnicodeDecodeError as e:
            # 捕获解码错误
            print(f"解码错误: {e}")
        except Exception as e:
            # 捕获其他所有错误
            print(f"读取串口数据时发生错误: {e}")

    def update_uart_output(self,str):
        print(str)

    def get_camera_id(self):
        # 尝试从多个 ID 中找到第一个有效的摄像头
        for camera_id in range(2):  # 假设最多有 10 个摄像头
            cap = cv2.VideoCapture(camera_id)
            if cap.isOpened():
                cap.release()
                print(f"Camera found at ID {camera_id}")
                return camera_id
        print("No camera found")
        return None  # 如果没有找到摄像头，则返回 None

    def SaveBackground(self):
            if self.camera_is_playing:
                ret, frame = self.cap.read()
                if ret:
                    Save_Background(frame)
                    self.log_message(f"保存背景成功: background.jpg")
                else:
                    self.log_message("保存背景失败")
            else:
                self.log_message("摄像头未工作，保存背景失败")

    def Reset_Accumulated(self):#超时清零
        most_frequent_category = max(self.accumulated_category_count, key=self.accumulated_category_count.get)
        self.accumulated_category_count.update({label: 0 for label in self.categories})
        num = self.categories.index(most_frequent_category)
        self.handle_action(num)
        self.categories_num = self.categories_num + 1
        self.text_uart.append(f"{self.categories_num} {self.categories[num]} 1 OK!")
        self.waitforcam()
        self.log_message(f"Most frequent category: {most_frequent_category} with count {self.accumulated_category_count[most_frequent_category]}")
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

    def display_uart_data(self, data):
        self.text_uart.append(data)

    def clear_text_edit(self):
        self.text_log.clear()

    def log_message(self, message):
        self.text_log.append(message)

    def StartRun(self):
            if self.camera_is_playing:
                pass
            else:
                if self.cap.isOpened():
                    self.cap.release()
                self.cap = cv2.VideoCapture(self.camera_id)
                self.log_message(f"Switched to camera: {self.camera_id}")
                self.camera_is_playing = True

    def update_gpio_values(self):
        gpio_values = self.gpio_reader.read_pin_states()
        labels = ["满载", "满载", "满载", "满载"]
        # "有害垃圾","厨余垃圾","其他垃圾","可回收垃圾"
        if self.Servo_Angle == 90:
            self.gpio_table.setItem(0, 0, QTableWidgetItem(labels[0] if gpio_values.get(self.gpios[3]) else f"未{labels[0]}"))
            self.gpio_table.setItem(1, 0, QTableWidgetItem(labels[1] if gpio_values.get(self.gpios[2]) else f"未{labels[1]}"))
            self.gpio_table.setItem(2, 0, QTableWidgetItem(labels[2] if gpio_values.get(self.gpios[1]) else f"未{labels[2]}"))
            self.gpio_table.setItem(3, 0, QTableWidgetItem(labels[3] if gpio_values.get(self.gpios[0]) else f"未{labels[3]}"))
        elif self.Servo_Angle == 180:
            self.gpio_table.setItem(0, 0, QTableWidgetItem(labels[0] if gpio_values.get(self.gpios[3]) else f"未{labels[0]}"))
            self.gpio_table.setItem(1, 0, QTableWidgetItem(labels[1] if gpio_values.get(self.gpios[2]) else f"未{labels[1]}"))
            self.gpio_table.setItem(2, 0, QTableWidgetItem(labels[2] if gpio_values.get(self.gpios[1]) else f"未{labels[2]}"))
            self.gpio_table.setItem(3, 0, QTableWidgetItem(labels[3] if gpio_values.get(self.gpios[0]) else f"未{labels[3]}"))
        elif self.Servo_Angle == 270:
            self.gpio_table.setItem(0, 0, QTableWidgetItem(labels[0] if gpio_values.get(self.gpios[2]) else f"未{labels[0]}"))
            self.gpio_table.setItem(1, 0, QTableWidgetItem(labels[1] if gpio_values.get(self.gpios[1]) else f"未{labels[1]}"))
            self.gpio_table.setItem(2, 0, QTableWidgetItem(labels[2] if gpio_values.get(self.gpios[0]) else f"未{labels[2]}"))
            self.gpio_table.setItem(3, 0, QTableWidgetItem(labels[3] if gpio_values.get(self.gpios[3]) else f"未{labels[3]}"))
        elif self.Servo_Angle == 0:
            self.gpio_table.setItem(0, 0, QTableWidgetItem(labels[0] if gpio_values.get(self.gpios[1]) else f"未{labels[0]}"))
            self.gpio_table.setItem(1, 0, QTableWidgetItem(labels[1] if gpio_values.get(self.gpios[4]) else f"未{labels[1]}"))
            self.gpio_table.setItem(2, 0, QTableWidgetItem(labels[2] if gpio_values.get(self.gpios[3]) else f"未{labels[2]}"))
            self.gpio_table.setItem(3, 0, QTableWidgetItem(labels[3] if gpio_values.get(self.gpios[2]) else f"未{labels[3]}"))


        states = gpio_values.get(26)
        if states == self.last2states and states != self.laststates:
            self.last2states = self.laststates
            self.laststates = states
            self.StartRun()
        if self.last2states == self.laststates:
            self.laststates = states
        print(f"引脚状态：{self.last2states} {self.laststates} {states}")

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
                num = self.accumulate_and_check_category_count(category_count)#满10次才会返回
                if num is not None:
                    self.handle_action(num)
                    self.categories_num = self.categories_num + 1
                    self.text_uart.append(f"{self.categories_num} {self.categories[num]} 1 OK!")
                    self.waitforcam()
                    self.accumulated_category_count.update({label: 0 for label in self.categories})
                self.log_message(f"Category counts: {self.accumulated_category_count}:{sum(self.accumulated_category_count.values())}")
                if(sum(self.accumulated_category_count.values())>0):
                    if self.is_running:#如果有东西并且电机还在移动
                        self.motor_stop()
                    if not self.Reset_timer_isOn: #如果定时器未开启则开启定时器
                        self.Reset_timer_isOn = True
                        self.Reset_timer.start(4000)#5s内检测完
                self.SendImage2Lable(frame_with_boxes)
        else:
            self.SendImage2Lable(frame)

    def waitforcam(self):
        self.cap.release()
        self.cap = cv2.VideoCapture(self.camera_id)
        self.accumulated_category_count.update({label: 0 for label in self.categories})

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
            if(not result):
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
