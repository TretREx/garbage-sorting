#include "FreeRTOS.h"
#include "task.h"
#include <stdio.h>

// 定义时间戳宏
#define GetTime()   xTaskGetTickCount()

// PID结构体定义
typedef struct {
    float Kp;             // 比例系数
    float Ki;             // 积分系数
    float Kd;             // 微分系数
    float setpoint;       // 目标值
    float integral;       // 积分项
    float previous_error; // 上一次误差
    float output;         // 输出值
    float output_min;     // 输出最小值
    float output_max;     // 输出最大值
    TickType_t last_time; // 上次计算时间
} PID_TypeDef;

// PID初始化函数
void PID_Init(PID_TypeDef *pid, float Kp, float Ki, float Kd, float setpoint, float output_min, float output_max);
float PID_Compute(PID_TypeDef *pid, float current_value);
