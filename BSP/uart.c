/*
串口功能：接收到垃圾信息,停止电机，控制舵机进行分拣
		 分拣完成恢复电机
*/
#include "uart.h"
#include"servo.h"
#include "motor.h"
TaskHandle_t 			UartHandle;//串口任务句柄
SemaphoreHandle_t UARTPRINTF_SemaphoreHandle;//串口保护互斥量保护

uint8_t rxdat;
uint8_t rx_p;
uint8_t rxdata[10];
bool rxflag;

void Uart_Task(void *argument)
{
    Uart_Config();  // 初始化 UART
    UartPrintf("Uart_Task Uart_flag:%d", __HAL_UART_GET_FLAG(&huart1, UART_FLAG_RXNE));

    UART_INFO uartData;  // 创建 UART_INFO 结构体实例

    while(1)
    {
        if(rxflag == 1)  // 成功接收数据
        {
            SaveUartData(rxdata,&uartData);
            PrintUartData(&uartData);

            if (uartData.header == HEADER && uartData.footer == FOOTER)
            {
                uint8_t calculatedChecksum = rxdata[1] | rxdata[2] | rxdata[3] | rxdata[4] | rxdata[5] | rxdata[6];

                if (calculatedChecksum == uartData.checksum)  // 校验通过进行相关设计
                {
                    if(uartData.command == SERVO_COMMAND)//如果是舵机控制
                    {
                        uint8_t ID = uartData.info[0]; // 获取舵机 ID
                        int angle = (uartData.info[1] << 24) | uartData.info[2]<<16 | uartData.info[3]<<8 | uartData.info[4];
                        Servo_SetAngle(ID, (uint16_t)angle); // 调用设置角度的函数
                        UartPrintf("Servo_ID: %d, angle: %d", ID, angle); // 打印舵机 ID 和角度
                    }
                    else if(uartData.command == MOTOR_COMMAND) // 如果是电机控制
                    {
                        uint8_t ID = uartData.info[0]; // 获取电机 ID
                        int speed = (uartData.info[1] << 24) | uartData.info[2]<<16 | uartData.info[3]<<8 | uartData.info[4];
                        switch(ID)
                        {
                            case 1:
                                PID_setMotorPoint(&motor1, (float)speed);
                                break;
                            case 2:
                                PID_setMotorPoint(&motor2, (float)speed);
                                break;
                            case 3:
                                PID_setMotorPoint(&motor3, (float)speed);
                                break;
                            case 4:
                                break;
                            default:
                                break;
                        }
                        UartPrintf("Motor_ID: %d, speed: %d", ID, speed); // 打印电机 ID 和速度
                    }
                    else if(uartData.command == MOTOR_COMPSPEED_COMMAND)//占空比补偿控制
                    {
                        uint8_t ID = uartData.info[0]; // 获取电机 ID
                        int comp = (uartData.info[1] << 24) | uartData.info[2]<<16 | uartData.info[3]<<8 | uartData.info[4];
                        switch(ID)
                        {
                            case 1:
                                Motor_SetCompSpeed(&motor1, comp);
                                break;
                            case 2:
                                Motor_SetCompSpeed(&motor2, comp);
                                break;
                            case 3:
                                Motor_SetCompSpeed(&motor3, comp);
                                break;
                            case 4:
                                Motor_SetCompSpeed(&motor4, comp);
                                break;
                            default:
                                break;
                        }
                        UartPrintf("Motor_ID: %d, Compspeed: %d", ID, comp); // 打印电机 ID 和速度
                    }
                    else if(uartData.command == ACTION_COMMAND)
                    {
                        uint8_t action_id = uartData.info[0];
                        switch (action_id)
                        {
                            case 0:
                                break;
                            case 1:
                                break;
                            case 2:
                                break;
                            case 3:
                                break;
                        }
                        UartPrintf("Action:%d",action_id);
                    }
                    else if(uartData.command==RESETTIME_COMMAND)
                    {
                        uint8_t ID = uartData.info[0]; // 获取电机 ID
                        int timer = (uartData.info[1] << 24) | uartData.info[2]<<16 | uartData.info[3]<<8 | uartData.info[4];
                        uint16_t time_id = uartData.info[1] << 8 |uartData.info[2];
                        uint16_t en = uartData.info[3] << 8 |uartData.info[4];
                        switch (ID)
                        {
                        case 1:
                            xTimerChangePeriod(xOneShotTimer1,timer,0);
                            motor1.ResetTime = timer;
                            break;
                        case 2:
                            xTimerChangePeriod(xOneShotTimer2,timer,0);
                            motor2.ResetTime = timer;
                            break;
                        case 3:
                            xTimerChangePeriod(xOneShotTimer3,timer,0);
                            motor3.ResetTime = timer;
                            break;
                        case 4://停止或开启全部电机
                            switch(time_id)
                            {
                                case 1:
                                    if(en)
                                    {
                                        xTimerReset(xOneShotTimer1,0);
                                    }
                                    else
                                    {
                                        xTimerStop(xOneShotTimer1,0);
                                    }
                                    break;
                                case 2:
                                    if(en)
                                    {
                                        xTimerReset(xOneShotTimer2,0);
                                    }
                                    else
                                    {
                                        xTimerStop(xOneShotTimer2,0);
                                    }
                                    break;
                                case 3:
                                    if(en)
                                    {
                                        xTimerReset(xOneShotTimer3,0);
                                    }
                                    else
                                    {
                                        xTimerStop(xOneShotTimer3,0);
                                    }
                                    break;
                            }
                            break;
                        case 5:
                            switch (time_id)
                            {
                            case 1:
                                xTimerChangePeriod(xOneShotTimer1,en,0);
                                motor1.ResetTime = en;
                                break;
                            case 2:
                                xTimerChangePeriod(xOneShotTimer2,en,0);
                                motor2.ResetTime = en;
                                break;
                            case 3:
                                xTimerChangePeriod(xOneShotTimer3,en,0);
                                motor3.ResetTime = en;
                                break;
                            default:
                                break;
                            }
                        default:
                            break;
                        }
                        UartPrintf("ResetTime:%d %d %d",motor1.ResetTime,motor2.ResetTime,motor3.ResetTime);
                    }
                }
                else  // 校验失败返回失败信息
                {
                    UartPrintf("Checksum error. Expected: 0x%02X, Received: 0x%02X\r\n", calculatedChecksum, uartData.checksum);
                }
            }
            else
            {
                UartPrintf("Invalid data format: Incorrect HEADER or FOOTER.\r\n");
            }
            rxflag = 0;
            Uart_Config();
        }
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}




static void UART_Printf(char *strings){		//	可以用sprintf()进行封装
	xSemaphoreTake(UARTPRINTF_SemaphoreHandle,portMAX_DELAY);//用互斥量进行保护
	HAL_UART_Transmit(&_USART,strings,strlen(strings),strlen(strings));
	HAL_UART_Transmit(&_USART,"\r\n",2,2);
	xSemaphoreGive(UARTPRINTF_SemaphoreHandle);
}

int UartPrintf(const char *format,...) {
       char buffer[64];
       va_list args;
       va_start(args, format);
       vsnprintf(buffer, sizeof(buffer), format, args);
       va_end(args);
       UART_Printf(buffer);
       return 0;
}


void Uart_Config(void)
{
	HAL_UART_Receive_IT(&_USART,&rxdat,1);
}

void Uart_Stop(void)
{
	__HAL_UART_DISABLE_IT(&_USART, UART_IT_RXNE);
}

void Uart_Start(void)
{
	__HAL_UART_ENABLE_IT(&_USART, UART_IT_RXNE);
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
	UBaseType_t uxSavedInterruptStatus; //关闭调度，保护串口
	uxSavedInterruptStatus = taskENTER_CRITICAL_FROM_ISR();
	if(huart->Instance == __USART)
	{
		if(rxflag == 0)
		{
			rxdata[rx_p++] = rxdat;
		}
		if(rx_p >= DATA_LENGTH)
		{
			rxflag = 1;
			rx_p = 0;
		}
		Uart_Config();
	}
	taskEXIT_CRITICAL_FROM_ISR( uxSavedInterruptStatus );
}

/**
 * @brief 保存接收到的数据到 UART_INFO 结构体
 *
 * @param rxdata 接收到的字节数组
 * @param uartData 保存数据的 UART_INFO 结构体
 */
void SaveUartData(uint8_t *rxdata, UART_INFO *uartData)
{
    uartData->header = rxdata[0];
    uartData->command = rxdata[1];
    uartData->info[0] = rxdata[2];
    uartData->info[1] = rxdata[3];
    uartData->info[2] = rxdata[4];
    uartData->info[3] = rxdata[5];
    uartData->info[4] = rxdata[6];
    uartData->checksum = rxdata[7];
    uartData->footer = rxdata[8];
}

/**
 * @brief 打印 UART_INFO 结构体中的数据
 *
 * @param uartData 要打印的 UART_INFO 结构体
 */
void PrintUartData(const UART_INFO *uartData)
{
    UartPrintf("Header: 0x%02X\r\n", uartData->header);
    UartPrintf("Command: 0x%02X\r\n", uartData->command);
    UartPrintf("Info: 0x%02X 0x%02X 0x%02X 0x%02X 0x%02X\r\n", uartData->info[0], uartData->info[1],
                                                             uartData->info[2],uartData->info[3],uartData->info[4]);
    UartPrintf("Checksum: 0x%02X\r\n", uartData->checksum);
    UartPrintf("Footer: 0x%02X\r\n", uartData->footer);
}
