/*
���ڹ��ܣ����յ�������Ϣ,ֹͣ��������ƶ�����зּ�
		 �ּ���ɻָ����
*/
#include "uart.h"
#include"servo.h"
#include "motor.h"
TaskHandle_t 			UartHandle;//����������
SemaphoreHandle_t UARTPRINTF_SemaphoreHandle;//���ڱ�������������

uint8_t rxdat;
uint8_t rx_p;
uint8_t rxdata[10];
bool rxflag;

void Uart_Task(void *argument)
{
    Uart_Config();  // ��ʼ�� UART
    UartPrintf("Uart_Task Uart_flag:%d", __HAL_UART_GET_FLAG(&huart1, UART_FLAG_RXNE));

    UART_INFO uartData;  // ���� UART_INFO �ṹ��ʵ��

    while(1)
    {
        if(rxflag == 1)  // �ɹ���������
        {
            SaveUartData(rxdata,&uartData);
            PrintUartData(&uartData);

            if (uartData.header == HEADER && uartData.footer == FOOTER)
            {
                uint8_t calculatedChecksum = rxdata[1] | rxdata[2] | rxdata[3] | rxdata[4] | rxdata[5] | rxdata[6];

                if (calculatedChecksum == uartData.checksum)  // У��ͨ������������
                {
                    if(uartData.command == SERVO_COMMAND)//����Ƕ������
                    {
                        uint8_t ID = uartData.info[0]; // ��ȡ��� ID
                        int angle = (uartData.info[1] << 24) | uartData.info[2]<<16 | uartData.info[3]<<8 | uartData.info[4];
                        Servo_SetAngle(ID, (uint16_t)angle); // �������ýǶȵĺ���
                        UartPrintf("Servo_ID: %d, angle: %d", ID, angle); // ��ӡ��� ID �ͽǶ�
                    }
                    else if(uartData.command == MOTOR_COMMAND) // ����ǵ������
                    {
                        uint8_t ID = uartData.info[0]; // ��ȡ��� ID
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
                        UartPrintf("Motor_ID: %d, speed: %d", ID, speed); // ��ӡ��� ID ���ٶ�
                    }
                    else if(uartData.command == MOTOR_COMPSPEED_COMMAND)//ռ�ձȲ�������
                    {
                        uint8_t ID = uartData.info[0]; // ��ȡ��� ID
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
                        UartPrintf("Motor_ID: %d, Compspeed: %d", ID, comp); // ��ӡ��� ID ���ٶ�
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
                        uint8_t ID = uartData.info[0]; // ��ȡ��� ID
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
                        case 4://ֹͣ����ȫ�����
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
                else  // У��ʧ�ܷ���ʧ����Ϣ
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




static void UART_Printf(char *strings){		//	������sprintf()���з�װ
	xSemaphoreTake(UARTPRINTF_SemaphoreHandle,portMAX_DELAY);//�û��������б���
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
	UBaseType_t uxSavedInterruptStatus; //�رյ��ȣ���������
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
 * @brief ������յ������ݵ� UART_INFO �ṹ��
 *
 * @param rxdata ���յ����ֽ�����
 * @param uartData �������ݵ� UART_INFO �ṹ��
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
 * @brief ��ӡ UART_INFO �ṹ���е�����
 *
 * @param uartData Ҫ��ӡ�� UART_INFO �ṹ��
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
