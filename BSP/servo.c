#include "servo.h"
#include "uart.h"

TaskHandle_t ServoHandle;

/* 舵机任务 */
void Servo_Task(void *argument)
{
	Servo_Config();//舵机初始化
	UartPrintf("Servo_Task");

	uint32_t value=0;
	while(1)
	{
        // Servo_SetAngle(3,0);
        // vTaskDelay(pdMS_TO_TICKS(4000));
        // Servo_SetAngle(3,90);
        // vTaskDelay(pdMS_TO_TICKS(2000));
        // Servo_SetAngle(3,180);
        // vTaskDelay(pdMS_TO_TICKS(2000));
        // Servo_SetAngle(3,270);
        vTaskDelay(pdMS_TO_TICKS(2000));
 	}
}


/*
	舵机设置
*/
void Servo_Config()
{
    HAL_TIM_PWM_Start(&SERVO3_TIM, SERVO3_CHANNEL);
    HAL_TIM_PWM_Start(&SERVO4_TIM, SERVO4_CHANNEL);
    Servo_SetAngle(3, 90);
    Servo_SetAngle(4, 0);

}

// 设置舵机角度，根据不同舵机的最大角度分开处理
void Servo_SetAngle(uint8_t servo, uint16_t angle) {
    float pulse_width = SERVO_MIN_PULSE;  // 初始化脉宽

    switch (servo) {
        case 1:
            if (angle > SERVO1_MAX_ANGLE) {
                angle = SERVO1_MAX_ANGLE;  // 限制角度最大为舵机1的最大角度
            }
            pulse_width = SERVO_MIN_PULSE + (SERVO_MAX_PULSE - SERVO_MIN_PULSE) *(float) angle / SERVO1_MAX_ANGLE;
            __HAL_TIM_SET_COMPARE(&htim3, SERVO1_CHANNEL, (uint32_t)pulse_width);
            break;

        case 2:
            if (angle > SERVO2_MAX_ANGLE) {
                angle = SERVO2_MAX_ANGLE;  // 限制角度最大为舵机2的最大角度
            }
            pulse_width = SERVO_MIN_PULSE + (SERVO_MAX_PULSE - SERVO_MIN_PULSE) * angle / SERVO2_MAX_ANGLE;
            __HAL_TIM_SET_COMPARE(&htim3, SERVO2_CHANNEL, pulse_width);
            break;

        case 3:
            if (angle > SERVO3_MAX_ANGLE) {
                angle = SERVO3_MAX_ANGLE;  // 限制角度最大为舵机3的最大角度
            }
            pulse_width = SERVO_MIN_PULSE + (SERVO_MAX_PULSE - SERVO_MIN_PULSE) * angle / SERVO3_MAX_ANGLE;
            __HAL_TIM_SET_COMPARE(&htim3, SERVO3_CHANNEL, pulse_width);
            break;

        case 4:
            if (angle > SERVO4_MAX_ANGLE) {
                angle = SERVO4_MAX_ANGLE;  // 限制角度最大为舵机4的最大角度
            }
            pulse_width = SERVO_MIN_PULSE + (SERVO_MAX_PULSE - SERVO_MIN_PULSE) * angle / SERVO4_MAX_ANGLE;
            __HAL_TIM_SET_COMPARE(&htim3, SERVO4_CHANNEL, pulse_width);
            break;

        default:
            break;
    }
}



