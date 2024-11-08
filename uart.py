import sys
import time
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QThread, pyqtSignal, QCoreApplication

class SerialThread(QThread):
    data_received = pyqtSignal(str)
    status_update = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.HEADER = 0x55
        self.FOOTER = 0xAA
        self.COMMAND_MOTOR_ANGLE = 0x01
        self.COMMAND_MOTOR_SPEED = 0x02
        self.COMMAND_COMPMOTOR_SPEED = 0x03
        self.COMMAND_ACTION_COMMAND = 0x04
        self.COMMAND_RESETTIME_COMMAND = 0x05

        self.serial_port = None
        self.baudrate = 115200
        self.available_ports = []
        self.connection_status = ""
        self.debug = True
        self.uart_running = False

    def configure_serial(self, baudrate):
        self.baudrate = baudrate

    def create_uart_packet(self, motor_id, info, command):
        info_bytes = [
            motor_id,
            (info >> 24) & 0xFF,
            (info >> 16) & 0xFF,
            (info >> 8) & 0xFF,
            info & 0xFF
        ]
        packet = {
            'header': self.HEADER,
            'command': command,
            'info': info_bytes,
            'checksum': 0,
            'footer': self.FOOTER
        }
        checksum = (packet['command'] | packet['info'][0] | packet['info'][1] | packet['info'][2] |
                    packet['info'][3] | packet['info'][4])
        packet['checksum'] = checksum
        return bytes([packet['header'], packet['command']] + packet['info'] + [packet['checksum'], packet['footer']])

    def send_uart_packet(self, motor_id, info, command):
        if not self.uart_running:
            print("串口未工作")
            return False
        packet = self.create_uart_packet(motor_id, info, command)
        hex_data = ' '.join(f"0x{byte:02X}" for byte in packet)
        if self.debug:
            print(f"发送数据包: {hex_data}")
        try:
            self.serial_port.write(packet)
        except serial.SerialException as e:
            if self.debug:
                print(f"发送数据包失败: {e}")
            return False
        time.sleep(0.1)
        return True

    def scan_ports(self):
        ports = serial.tools.list_ports.comports()
        self.available_ports = [port.device for port in ports]
        return self.available_ports

    def connect_to_port(self, port):
        self.serial_port = serial.Serial(port=port, baudrate=self.baudrate, timeout=1)
        self.uart_running = True

    def uart_stop(self):
        self.serial_port.close()
        self.uart_running = False

    def uart_start(self):
        self.uart_running = True

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    serial_thread = SerialThread()
    serial_thread.scan_ports()
    if serial_thread.available_ports:
        serial_thread.connect_to_port(serial_thread.available_ports[0])
        success = serial_thread.send_uart_packet(3, 0, serial_thread.COMMAND_MOTOR_SPEED)
        if success:
            print("命令发送成功.")
        else:
            print("命令发送失败.")
    serial_thread.uart_stop()
    sys.exit(app.exec_())
