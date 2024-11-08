#ifndef __UART_H
#define __UART_H
	#include "FreeRTOS.h"
	#include "task.h"
	#include "main.h"
	#include "cmsis_os.h"
	#include "usart.h"
	#include <stdarg.h>
	#include "semphr.h"
	#include "stdio.h"
	#include "string.h"
	#include "stdbool.h"
	#include "stdlib.h"
	extern SemaphoreHandle_t UARTPRINTF_SemaphoreHandle;
	extern TaskHandle_t 			UartHandle;
	extern uint8_t rxdat;
	extern uint8_t rx_p;
	extern uint8_t rxdata[10];
	extern bool rxflag;

	#define _USART huart1
	#define __USART USART1
	#define DATA_LENGTH 9
	#define HEADER 0x55
	#define FOOTER 0xAA
	#define SERVO_COMMAND 0x01
	#define MOTOR_COMMAND 0x02
	#define MOTOR_COMPSPEED_COMMAND 0x03
	#define ACTION_COMMAND 0x04
	#define RESETTIME_COMMAND 0x05

	typedef struct UART_INFO
	{
		uint8_t header;
		uint8_t command;
		uint8_t info[5];
		uint8_t checksum;
		uint8_t footer;
	} UART_INFO;



	int UartPrintf(const char *format,...);
	void Uart_Config(void);
	void Uart_Stop(void);
	void Uart_Start(void);

	void Uart_Task(void *argument);
	void SaveUartData(uint8_t *rxdata, UART_INFO *uartData);
	void PrintUartData(const UART_INFO *uartData);

#endif
