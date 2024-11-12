# QT GUI界面
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QTextEdit, QComboBox, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

class MYGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("垃圾分类实验")  # "Garbage Classification Experiment"
        self.setFixedSize(1024, 600)
        self.setStyleSheet("background-color:  #00FF00;")
        # 创建一个表格来显示垃圾状态
        self.gpio_table = QTableWidget(self)
        self.gpio_table.setStyleSheet("font-size: 10pt;")  # Set font size for UART text box
        self.gpio_table.setFixedSize(200, 125)
        self.gpio_table.setGeometry(700, 400, 200, 125)  # 调整位置和大小
        self.gpio_table.setRowCount(4)  # 行数为 4（四种垃圾）
        self.gpio_table.setColumnCount(1)  # 列数为 1
        self.gpio_table.setHorizontalHeaderLabels(["垃圾满载状态"])  # 设置表头
        self.gpio_table.setVerticalHeaderLabels([
            "有害垃圾",
            "厨余垃圾",
            "其他垃圾",
            "可回收垃圾"
        ])  # 设置垂直表头

        self.gpio_table.setRowHeight(0, 25)
        self.gpio_table.setRowHeight(1, 25)
        self.gpio_table.setRowHeight(2, 25)
        self.gpio_table.setRowHeight(3, 25)

        self.video_label = QLabel(self)
        self.video_size = (480, 320)
        self.video_label.setFixedSize(self.video_size[0], self.video_size[1])
        self.video_label.setGeometry(60, 20, self.video_size[0], self.video_size[1])

        self.play_button = QPushButton("暂停", self)  # "Start" in Chinese
        self.play_button.setFixedSize(50, 30)
        self.play_button.setGeometry(60, self.video_size[1] + 20, 50, 30)

        self.switch_button = QPushButton("切换", self)  # "Switch" in Chinese
        self.switch_button.setFixedSize(50, 30)
        self.switch_button.setGeometry(self.video_size[0] + 60 - 50, self.video_size[1] + 20, 50, 30)

        self.text_uart = QTextEdit("", self)
        self.text_uart_size = (300,200)
        self.text_uart.setReadOnly(True)
        self.text_uart.setStyleSheet("font-size: 10pt;")  # Set font size for UART text box
        self.text_uart.setFixedSize( self.text_uart_size[0],  self.text_uart_size[1])
        self.text_uart.setGeometry(650, 50,  self.text_uart_size[0], self.text_uart_size[1])

        # Create a dropdown for serial port selection
        self.port_combo = QComboBox(self)
        self.port_combo.setGeometry(650, 10, 120, 30)

        # Create connect button
        self.connect_button = QPushButton("连接串口", self)  # "Connect Serial Port"
        self.connect_button.setGeometry(800, 10, 120, 30)

        self.text_log = QTextEdit("", self)
        self.text_log.setReadOnly(True)
        self.text_log.setStyleSheet("font-size: 10pt;")    # Set font size for log text box
        self.text_log.setFixedSize(640, 100)
        self.text_log.setGeometry(20, 400, 480, 100)

        self.clear_button = QPushButton('Clear', self)  # "Clear Text" in Chinese
        self.clear_button.setFixedSize(100, 30)
        self.clear_button.setGeometry(300, self.video_size[1] + 20, 100, 30)

        self.action_button_size = (60,25)

        self.action1_button = QPushButton("Action1", self)  # "Start" in Chinese
        self.action1_button.setFixedSize(self.action_button_size[0], self.action_button_size[1])
        self.action1_button.setGeometry(650, 310 , self.action_button_size[0], self.action_button_size[1])

        self.action2_button = QPushButton("Action2", self)  # "Start" in Chinese
        self.action2_button.setFixedSize(self.action_button_size[0], self.action_button_size[1])
        self.action2_button.setGeometry(650+70, 310 , self.action_button_size[0], self.action_button_size[1])

        self.action3_button = QPushButton("Action3", self)  # "Start" in Chinese
        self.action3_button.setFixedSize(self.action_button_size[0], self.action_button_size[1])
        self.action3_button.setGeometry(650+70*2, 310 ,self.action_button_size[0], self.action_button_size[1])

        self.action4_button = QPushButton("Action4", self)  # "Start" in Chinese
        self.action4_button.setFixedSize(self.action_button_size[0], self.action_button_size[1])
        self.action4_button.setGeometry(650+70*3, 310 ,self.action_button_size[0], self.action_button_size[1])

        self.Reset_button = QPushButton("Reset", self)  # "Start" in Chinese
        self.Reset_button.setFixedSize(self.action_button_size[0], self.action_button_size[1])
        self.Reset_button.setGeometry(650, 345 , self.action_button_size[0], self.action_button_size[1])

        self.Save_button = QPushButton("Save_B", self)  # "Start" in Chinese
        self.Save_button.setFixedSize(self.action_button_size[0], self.action_button_size[1])
        self.Save_button.setGeometry(650+70, 345 , self.action_button_size[0], self.action_button_size[1])

        self.Start = QPushButton("Start", self)  # "Start" in Chinese
        self.Start.setFixedSize(self.action_button_size[0], self.action_button_size[1])
        self.Start.setGeometry(840, 345 , self.action_button_size[0], self.action_button_size[1])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MYGUI()
    player.show()
    sys.exit(app.exec_())
