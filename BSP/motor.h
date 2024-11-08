#ifndef __MOTOR_H
#define __MOTOR_H
	#include "FreeRTOS.h"
	#include "task.h"
	#include "main.h"
	#include "cmsis_os.h"
	#include "main.h"
	#include "tim.h"
	#include "semphr.h"
	#include "timers.h"
	#include "stdbool.h"
	#include "pid.h"
	#include "math.h"

	extern	int SPEED1;
	extern	int SPEED2;
	extern	int SPEED3;

	#define NUM_Lights 3

	/*               引脚设置               */
	#define PWM_MAX_VALUE 999

	#define MOTOR1_TIM TIM2
	#define MOTOR1_CHANNEL TIM_CHANNEL_1
	#define MOTOR1_PORT	GPIOB
	#define MOTOR1_PIN1	GPIO_PIN_3
	#define MOTOR1_PIN2 GPIO_PIN_4

	#define MOTOR2_TIM TIM2
	#define MOTOR2_CHANNEL TIM_CHANNEL_2
	#define MOTOR2_PORT	GPIOB
	#define MOTOR2_PIN1	GPIO_PIN_5
	#define MOTOR2_PIN2 GPIO_PIN_6

	#define MOTOR3_TIM TIM2
	#define MOTOR3_CHANNEL TIM_CHANNEL_3
	#define MOTOR3_PORT	GPIOB
	#define MOTOR3_PIN1	GPIO_PIN_7
	#define MOTOR3_PIN2 GPIO_PIN_8

	#define MOTOR4_TIM TIM2
	#define MOTOR4_CHANNEL TIM_CHANNEL_4
	#define MOTOR4_PORT	GPIOC
	#define MOTOR4_PIN1	GPIO_PIN_13
	#define MOTOR4_PIN2 GPIO_PIN_14


	#define MOTOR1_ENCODEA_PORT 		GPIOB
	#define MOTOR1_ENCODEA_EXTI_PIN 	GPIO_PIN_11
	#define MOTOR1_ENCODEB_PORT 		GPIOB
	#define MOTOR1_ENCODEB_PIN 			GPIO_PIN_10

	#define MOTOR2_ENCODEA_PORT 		GPIOB
	#define MOTOR2_ENCODEA_EXTI_PIN 	GPIO_PIN_12
	#define MOTOR2_ENCODEB_PORT 		GPIOB
	#define MOTOR2_ENCODEB_PIN 			GPIO_PIN_13

	#define MOTOR3_ENCODEA_PORT 		GPIOB
	#define MOTOR3_ENCODEA_EXTI_PIN 	GPIO_PIN_15
	#define MOTOR3_ENCODEB_PORT 		GPIOB
	#define MOTOR3_ENCODEB_PIN 			GPIO_PIN_14

	#define MOTOR4_ENCODEA_PORT			GPIOA
	#define MOTOR4_ENCODEA_EXTI_PIN 	GPIO_PIN_8
	#define MOTOR4_ENCODEB_PORT 		GPIOA
	#define MOTOR4_ENCODEB_PIN 			GPIO_PIN_11
/****************************************************/

	typedef enum {
		MOTOR_FORWARD,
		MOTOR_BACKWARD
	} MotorDirection;

	typedef struct
	{
		uint8_t flag;
		uint8_t step;
		uint8_t state;
	}KEY;

	typedef struct
	{
		int timers;//编码器计数值
		int CompSpeed;//速度补偿
		int _SPEED;
		float speed;//实际速度
		bool state;//实际转向
		PID_TypeDef TPID;//PID相关设置
		float pv2c;//速度到占空比的比例
		uint32_t ResetTime;
	}MOTOR;


	extern SemaphoreHandle_t xMotorSemaphore[NUM_Lights];
	extern TimerHandle_t xOneShotTimer1;
	extern TimerHandle_t xOneShotTimer2;
	extern TimerHandle_t xOneShotTimer3;
	extern TimerHandle_t KeyTimerHandle;
	extern TimerHandle_t SpeedGetHandle;
	extern xTaskHandle MotorHandle;

	extern MOTOR motor1;
	extern MOTOR motor2;
	extern MOTOR motor3;
	extern MOTOR motor4;

	void Motor_Task(void *argument);//电机任务
	void vONEShotTimerFunc1( TimerHandle_t xTimer );//红外对射函数
	void vONEShotTimerFunc2( TimerHandle_t xTimer );
	void vONEShotTimerFunc3( TimerHandle_t xTimer );
	void KeyTimerFunc( TimerHandle_t xTimer );//红外对射检测函数

	void Motor_SetCompSpeed(MOTOR *motor,uint16_t speed);//速度补偿
	void Motor_Config();//电机初始化
	void Motor_SetSpeed(uint8_t motor, float speed);
	void Motor_stop(uint8_t motor);
	void Motor_start(uint8_t motor);
	void SpeedSetTimerFun( TimerHandle_t xTimer );
	void PID_setMotorPoint(MOTOR *motor,float speed);
#endif


