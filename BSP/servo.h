#ifndef __SERVO_H
#define __SERVO_H

#include "FreeRTOS.h"
#include "task.h"
#include "main.h"
#include "cmsis_os.h"
#include "main.h"
#include "tim.h"

// 舵机相关定义
#define SERVO_AUTORELOAD (20000-1) // PWM周期 20ms
#define SERVO_MIN_PULSE 500        // 最小脉宽对应0度，0.5ms
#define SERVO_MAX_PULSE 2500       // 最大脉宽对应180度，2.5ms

// 舵机1相关的定时器和通道定义
#define SERVO1_TIM htim3
#define SERVO1_CHANNEL TIM_CHANNEL_1
#define SERVO1_MAX_ANGLE 180  // 舵机1的最大角度

// 舵机2相关的定时器和通道定义
#define SERVO2_TIM htim3
#define SERVO2_CHANNEL TIM_CHANNEL_2
#define SERVO2_MAX_ANGLE 180   // 舵机2的最大角度

// 舵机3相关的定时器和通道定义
#define SERVO3_TIM htim3
#define SERVO3_CHANNEL TIM_CHANNEL_3
#define SERVO3_MAX_ANGLE 270  // 舵机3的最大角度

// 舵机4相关的定时器和通道定义
#define SERVO4_TIM htim3
#define SERVO4_CHANNEL TIM_CHANNEL_4
#define SERVO4_MAX_ANGLE 180  // 舵机4的最大角度

extern TaskHandle_t ServoHandle;


void Servo_Config();
void Servo_SetAngle(uint8_t servo, uint16_t angle);
void Servo_Task(void *argument);


#endif


