from uart import *  # 假设 uart 是一个自定义的串口通信模块
import time
from image import compare_images3
class STM32CONTROL(SerialThread):
    def __init__(self):
        super().__init__()
        self.Servo_Angle = 0
        self.Servo_Target_Angle = 0
        self.is_running = False

    def action1(self):
        if not self.uart_running:  # 检查是否连接
            self.Log_Text("错误: 未连接串口.")
            return
        self.motor_stop()
        self.Servo_Target_Angle = 0
        timer = abs(self.Servo_Angle - self.Servo_Target_Angle)
        success = self.send_uart_packet(3, 0, self.COMMAND_MOTOR_ANGLE)
        if not success:
            self.Log_Text("错误: 动作 1 的 UART 数据包发送失败.")
            return
        time.sleep(timer / 90)
        self.Log_Text(f"执行动作 1,目标角度{self.Servo_Target_Angle},当前角度{self.Servo_Angle},所需时间{timer / 90}")
        self.take_out()

    def action2(self):
        if not self.uart_running:  # 检查是否连接
            self.Log_Text("错误: 未连接串口.")
            return
        self.motor_stop()
        self.Servo_Target_Angle = 90
        timer = abs(self.Servo_Angle - self.Servo_Target_Angle)
        success = self.send_uart_packet(3, 90, self.COMMAND_MOTOR_ANGLE)
        if not success:
            self.Log_Text("错误: 动作 2 的 UART 数据包发送失败.")
            return
        time.sleep(timer / 90)
        self.Log_Text(f"执行动作 2,目标角度{self.Servo_Target_Angle},当前角度{self.Servo_Angle},所需时间{timer / 90}")
        self.take_out()

    def action3(self):
        if not self.uart_running:  # 检查是否连接
            self.Log_Text("错误: 未连接串口.")
            return
        self.motor_stop()
        self.Servo_Target_Angle = 180
        timer = abs(self.Servo_Angle - self.Servo_Target_Angle)
        success = self.send_uart_packet(3, 180, self.COMMAND_MOTOR_ANGLE)
        if not success:
            self.Log_Text("错误: 动作 3 的 UART 数据包发送失败.")
            return
        time.sleep(timer / 90)
        self.Log_Text(f"执行动作 3,目标角度{self.Servo_Target_Angle},当前角度{self.Servo_Angle},所需时间{timer / 90}")
        self.take_out()

    def action4(self):
        if not self.uart_running:  # 检查是否连接
            self.Log_Text("错误: 未连接串口.")
            return
        self.motor_stop()
        self.Servo_Target_Angle = 270
        timer = abs(self.Servo_Angle - self.Servo_Target_Angle)
        success = self.send_uart_packet(3, 270, self.COMMAND_MOTOR_ANGLE)
        if not success:
            self.Log_Text("错误: 动作 4 的 UART 数据包发送失败.")
            return
        time.sleep(timer / 90)
        self.Log_Text(f"执行动作 4,目标角度{self.Servo_Target_Angle},当前角度{self.Servo_Angle},所需时间{timer / 90}")
        self.take_out()

    def take_out(self):
        if not self.uart_running:  # 检查是否连接
            self.Log_Text("错误: 未连接串口.")
            return
        self.Servo_Angle = self.Servo_Target_Angle
        success = self.send_uart_packet(4, 90, self.COMMAND_MOTOR_ANGLE)
        if not success:
            self.Log_Text("错误: 取出操作的 UART 数据包发送失败.")
            return
        time.sleep(1)
        success = self.send_uart_packet(4, 0, self.COMMAND_MOTOR_ANGLE)
        if not success:
            self.Log_Text("错误: 取出重置的 UART 数据包发送失败.")
            return
        time.sleep(1)
        self.motor_start()

    def Compress(self,num):
        self.send_uart_packet(4, num, self.COMMAND_MOTOR_SPEED)#压缩

    def Reset(self):
        if not self.uart_running:  # 检查是否连接
            self.Log_Text("错误: 未连接串口.")
            return
        self.send_uart_packet(1, 0, self.COMMAND_MOTOR_SPEED)
        self.send_uart_packet(2, 0, self.COMMAND_MOTOR_SPEED)
        self.send_uart_packet(3, 0, self.COMMAND_MOTOR_SPEED)
        self.Servo_Angle = 0
        self.send_uart_packet(3, 0, self.COMMAND_MOTOR_ANGLE)
        self.send_uart_packet(4, 0, self.COMMAND_MOTOR_ANGLE)
        self.is_running = False

    def motor_stop(self):
        if not self.uart_running:  # 检查是否连接
            self.Log_Text("错误: 未连接串口.")
            return
        self.send_uart_packet(1, 0, self.COMMAND_MOTOR_SPEED)
        self.send_uart_packet(2, 0, self.COMMAND_MOTOR_SPEED)
        self.send_uart_packet(3, 0, self.COMMAND_MOTOR_SPEED)
        self.is_running = False

    def motor_start(self):
        if not self.uart_running:  # 检查是否连接
            self.Log_Text("错误: 未连接串口.")
            return
        self.send_uart_packet(1, 6, self.COMMAND_MOTOR_SPEED)
        self.send_uart_packet(2, 6, self.COMMAND_MOTOR_SPEED)
        self.send_uart_packet(3, 5, self.COMMAND_MOTOR_SPEED)
        self.is_running = True

    def Stop_Reset_Time(self, motor_id):
        if not self.uart_running:  # 检查是否连接
            self.Log_Text("错误: 未连接串口.")
            return
        info = (0x00 << 24) | (motor_id << 16) | (0x00 << 8) | 0x00
        success = self.send_uart_packet(4, info, self.COMMAND_RESETTIME_COMMAND)
        if not success:
            self.Log_Text(f"错误: 无法重置电机 {motor_id} 的时间.")

    def Start_Reset_Time(self, motor_id):
        if not self.uart_running:  # 检查是否连接
            self.Log_Text("错误: 未连接串口.")
            return
        info = (0x00 << 24) | (motor_id << 16) | (0x00 << 8) | 0x01
        success = self.send_uart_packet(4, info, self.COMMAND_RESETTIME_COMMAND)
        if not success:
            self.Log_Text(f"错误: 无法启动电机 {motor_id} 的重置时间.")

    def Set_Reset_Time(self, motor_id, time):
        if not self.uart_running:  # 检查是否连接
            self.Log_Textself.Log_Text("错误: 未连接串口.")
            return
        time_high = (time >> 8) & 0xFF
        time_low = time & 0xFF
        info = (0x00 << 24) | (motor_id << 16) | (time_high << 8) | time_low
        success = self.send_uart_packet(5, info, self.COMMAND_RESETTIME_COMMAND)
        if not success:
            self.Log_Text(f"错误: 无法设置电机 {motor_id} 的重置时间.")

    def Log_Text(self,str):
        print(str)

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    controller = STM32CONTROL()
    controller.scan_ports()  # 扫描可用串口
    controller.connect_to_port(controller.available_ports[0])
    controller.action1()  # 执行动作 1
    controller.action2()  # 执行动作 2
    controller.action3()  # 执行动作 3
    controller.action4()  # 执行动作 4
    controller.take_out()  # 执行取出操作
    controller.Reset()  # 重置所有设置和电机
    sys.exit(app.exec_())
