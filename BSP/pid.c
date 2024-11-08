#include "pid.h"
#include "math.h"

// PID初始化函数
void PID_Init(PID_TypeDef *pid, float Kp, float Ki, float Kd, float setpoint, float output_min, float output_max) {
    pid->Kp = Kp;
    pid->Ki = Ki;
    pid->Kd = Kd;
    pid->setpoint = setpoint;
    pid->integral = 0.0f;
    pid->previous_error = 0.0f;
    pid->output = 0.0f;
    pid->output_min = output_min;
    pid->output_max = output_max;
    pid->last_time = GetTime();
}

// PID计算函数
float PID_Compute(PID_TypeDef *pid, float current_value) {
    TickType_t now = GetTime();
    float time_change = now - pid->last_time;

    if (time_change == 0) {
        return pid->output; // 避免时间变化为零导致除零错误
    }
    // 计算误差
    float error = pid->setpoint - current_value;

    // 计算积分项
    pid->integral += error * time_change;
   if (pid->integral > pid->output_max) {
        pid->integral = pid->output_max;
    } else if (pid->integral < pid->output_min) {
        pid->integral = pid->output_min;
    }
    // 计算微分项
    float derivative = (error - pid->previous_error) / time_change;
    // 计算输出
    pid->output = pid->Kp * error + pid->Ki * pid->integral + pid->Kd * derivative;

    // 设置输出限幅
    if (pid->output > pid->output_max) {
        pid->output = pid->output_max;
    } else if (pid->output < pid->output_min) {
        pid->output = pid->output_min;
    }

    // 更新状态
    pid->previous_error = error;
    pid->last_time = now;

    return pid->output;
}
