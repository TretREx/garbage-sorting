main.py 主程序运行入口,继承了下位机动作指令和串口协议  
cap.py 用于拍背景  
GUI.py QT基本画面组件  
images.py 用于进行图片比对,判断画面是否改变  
mygpio.py 用于jetson nano读取引脚电平  
uart.py 底层串口协议通讯  
stm32.py 继承uart.py用于给下位机发送动作指令  
yolov7_inference.py yolo推理接口  
