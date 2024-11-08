#include "motor.h"
#include "uart.h"

/*******任务句柄*********/
xTaskHandle MotorHandle;

SemaphoreHandle_t xMotorSemaphore[3];

/* 三级红外对射定时器 */
TimerHandle_t xOneShotTimer1;
TimerHandle_t xOneShotTimer2;
TimerHandle_t xOneShotTimer3;

/* 对射检测定时器 */
TimerHandle_t KeyTimerHandle;

/* 获取传送带速度定时器 */
TimerHandle_t SpeedGetHandle;
/* 对射定义 */
KEY key[NUM_Lights];
MOTOR motor1;
MOTOR motor2;
MOTOR motor3;
MOTOR motor4;


void Motor_Task(void *argument)
{

	Motor_Config();//电机初始化

	motor1._SPEED = 500;//设置速度补偿
	motor2._SPEED = 600;
	motor3._SPEED = 350;

	motor1.ResetTime = 2000;
	motor2.ResetTime = 2000;
	motor3.ResetTime = 2000;

	xTimerChangePeriod(xOneShotTimer1,motor1.ResetTime,0);
	xTimerChangePeriod(xOneShotTimer1,motor1.ResetTime,0);
	xTimerChangePeriod(xOneShotTimer1,motor1.ResetTime,0);

	motor1.CompSpeed = motor1._SPEED;
	motor2.CompSpeed = motor2._SPEED;
	motor3.CompSpeed = motor3._SPEED;

	xTimerStart(SpeedGetHandle,0);
	xTimerStart(KeyTimerHandle,0);

	UartPrintf("Motor Task");
	PID_Init(&motor1.TPID,1 ,0.1,0.05,0,-999,999 );
	PID_Init(&motor2.TPID,1 ,0.5,0.05,0,-999,999);
	PID_Init(&motor3.TPID,1 ,0.5,0.05,0,-999,999);

	uint8_t timers = 0;
	while(1)
	{
		timers++;
		if(timers == 10)
		{
			UartPrintf("M1:T:%0.2f,O:%0.2f,V:%0.2f,C:%03d,I:%0.2f,E:%0.2f",
						motor1.TPID.setpoint,motor1.TPID.output,motor1.speed,
						motor1.CompSpeed,motor1.TPID.integral*motor1.TPID.Ki,motor1.TPID.previous_error*motor1.TPID.Kp);

			UartPrintf("M2:T:%0.2f,O:%0.2f,V:%0.2f,C:%03d,I:%0.2f,E:%0.2f",
						motor2.TPID.setpoint,motor2.TPID.output,motor2.speed,
						motor2.CompSpeed,motor2.TPID.integral*motor2.TPID.Ki,motor2.TPID.previous_error*motor2.TPID.Kp);

			UartPrintf("M3:T:%0.2f,O:%0.2f,V:%0.2f,C:%03d,I:%0.2f,E:%0.2f",
						motor3.TPID.setpoint,motor3.TPID.output,motor3.speed,
						motor3.CompSpeed,motor3.TPID.integral*motor3.TPID.Ki,motor3.TPID.previous_error*motor3.TPID.Kp);

			timers = 0;
		}


		if(key[0].flag)
		{
			PID_setMotorPoint(&motor1,-1*fabs(motor1.TPID.setpoint));
			vTaskDelay(pdMS_TO_TICKS(500));
			Motor_stop(1);
			xTimerReset(xOneShotTimer1,0);
			key[0].flag =0;
		}
		if(key[1].flag)
		{
			Motor_stop(1);
			PID_setMotorPoint(&motor2,-1*fabs(motor2.TPID.setpoint));
			vTaskDelay(pdMS_TO_TICKS(500));
			Motor_stop(2);
			xTimerReset(xOneShotTimer1,0);
			xTimerReset(xOneShotTimer2,0);
            key[1].flag =0;
        }
		if(key[2].flag)
		{
			Motor_stop(1);
			Motor_stop(2);
			PID_setMotorPoint(&motor3,-1*fabs(motor3.TPID.setpoint));
			vTaskDelay(pdMS_TO_TICKS(500));
			Motor_stop(3);
			vTaskDelay(pdMS_TO_TICKS(2000));
			xTimerReset(xOneShotTimer1,0);
			xTimerReset(xOneShotTimer2,0);
			xTimerReset(xOneShotTimer3,0);
            key[2].flag =0;
		}
		vTaskDelay(pdMS_TO_TICKS(20));
	}
}

//电机速度初始化设置
void Motor_Config()
{
	Motor_SetSpeed(1,0);
	Motor_SetSpeed(2,0);
	Motor_SetSpeed(3,0);
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_2);
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_3);
}


// 设置电机的方向和速度
void Motor_SetSpeed(uint8_t motor,float speed) {
	uint16_t _speed = fabs(speed);
	if(_speed>PWM_MAX_VALUE) _speed = PWM_MAX_VALUE;
    switch (motor) {
        case 1:
            if (speed > 0) {
                HAL_GPIO_WritePin(MOTOR1_PORT, MOTOR1_PIN1, GPIO_PIN_SET);
                HAL_GPIO_WritePin(MOTOR1_PORT, MOTOR1_PIN2, GPIO_PIN_RESET);
            	__HAL_TIM_SET_COMPARE(&htim2, MOTOR1_CHANNEL, _speed);
            } else {
                HAL_GPIO_WritePin(MOTOR1_PORT, MOTOR1_PIN1, GPIO_PIN_RESET);
                HAL_GPIO_WritePin(MOTOR1_PORT, MOTOR1_PIN2, GPIO_PIN_SET);
            	__HAL_TIM_SET_COMPARE(&htim2, MOTOR1_CHANNEL, _speed);
            }
            break;
		case 2:
		    if (speed > 0) {
				HAL_GPIO_WritePin(MOTOR2_PORT, MOTOR2_PIN1, GPIO_PIN_SET);
				HAL_GPIO_WritePin(MOTOR2_PORT, MOTOR2_PIN2, GPIO_PIN_RESET);
				__HAL_TIM_SET_COMPARE(&htim2, MOTOR2_CHANNEL, _speed);
				} else {
                HAL_GPIO_WritePin(MOTOR2_PORT, MOTOR2_PIN1, GPIO_PIN_RESET);
                HAL_GPIO_WritePin(MOTOR2_PORT, MOTOR2_PIN2, GPIO_PIN_SET);
                __HAL_TIM_SET_COMPARE(&htim2, MOTOR2_CHANNEL, _speed);
				}
				break;
		case 3:
			if (speed > 0) {
				HAL_GPIO_WritePin(MOTOR3_PORT, MOTOR3_PIN1, GPIO_PIN_SET);
				HAL_GPIO_WritePin(MOTOR3_PORT, MOTOR3_PIN2, GPIO_PIN_RESET);
				__HAL_TIM_SET_COMPARE(&htim2, MOTOR3_CHANNEL, _speed);
				} else {
				HAL_GPIO_WritePin(MOTOR3_PORT, MOTOR3_PIN1, GPIO_PIN_RESET);
				HAL_GPIO_WritePin(MOTOR3_PORT, MOTOR3_PIN2, GPIO_PIN_SET);
				__HAL_TIM_SET_COMPARE(&htim2, MOTOR3_CHANNEL, _speed);
				}
		case 4:
			if (speed > 0) {
				HAL_GPIO_WritePin(MOTOR4_PORT, MOTOR4_PIN1, GPIO_PIN_SET);
				HAL_GPIO_WritePin(MOTOR4_PORT, MOTOR4_PIN2, GPIO_PIN_RESET);
				__HAL_TIM_SET_COMPARE(&htim2, MOTOR4_CHANNEL, _speed);
				} else {
                HAL_GPIO_WritePin(MOTOR4_PORT, MOTOR4_PIN1, GPIO_PIN_RESET);
                HAL_GPIO_WritePin(MOTOR4_PORT, MOTOR4_PIN2, GPIO_PIN_SET);
                __HAL_TIM_SET_COMPARE(&htim2, MOTOR4_CHANNEL, _speed);
				}
    }
}

void Motor_stop(uint8_t motor)
{
    switch (motor) {
        case 1:
            HAL_TIM_PWM_Stop(&htim2,TIM_CHANNEL_1);
            break;
		case 2:
			HAL_TIM_PWM_Stop(&htim2,TIM_CHANNEL_2);
            break;
        case 3:
            HAL_TIM_PWM_Stop(&htim2,TIM_CHANNEL_3);
            break;
		case 4:
			HAL_TIM_PWM_Stop(&htim2,TIM_CHANNEL_4);
            break;
    }
}

void Motor_start(uint8_t motor)
{
    switch (motor) {
        case 1:
            HAL_TIM_PWM_Start(&htim2,TIM_CHANNEL_1);
            break;
		case 2:
			HAL_TIM_PWM_Start(&htim2,TIM_CHANNEL_2);
            break;
        case 3:
            HAL_TIM_PWM_Start(&htim2,TIM_CHANNEL_3);
            break;
		case 4:
			HAL_TIM_PWM_Start(&htim2,TIM_CHANNEL_4);
            break;
    }
}

void vONEShotTimerFunc1( TimerHandle_t xTimer ) //第一级传送带
{
	BaseType_t xReturn = xSemaphoreTakeFromISR(xMotorSemaphore[0],0);
	if(xReturn == pdTRUE)
	{
		Motor_start(1);
		PID_setMotorPoint(&motor1,fabs(motor1.TPID.setpoint));
		xSemaphoreGiveFromISR(xMotorSemaphore[0],NULL);
	}
	else
	{
		UartPrintf("Get semaphore failed1");
	}
}
void vONEShotTimerFunc2( TimerHandle_t xTimer ) //第二级传送带
{
	BaseType_t xReturn = xSemaphoreTakeFromISR(xMotorSemaphore[1],0);
	if(xReturn == pdTRUE)
	{
		Motor_start(2);
		PID_setMotorPoint(&motor2,fabs(motor2.TPID.setpoint));
		xSemaphoreGiveFromISR(xMotorSemaphore[1],NULL);
	}
	else{
		UartPrintf("Get semaphore failed2");
	}
}
void vONEShotTimerFunc3( TimerHandle_t xTimer ) //第三级传送带
{
	BaseType_t xReturn = xSemaphoreTakeFromISR(xMotorSemaphore[2],0);
	if(xReturn == pdTRUE)
	{
		Motor_start(3);
		PID_setMotorPoint(&motor3,fabs(motor3.TPID.setpoint));
		xSemaphoreGiveFromISR(xMotorSemaphore[2],NULL);
	}
	else{
		UartPrintf("Get semaphore failed3");
	}
}
void KeyTimerFunc( TimerHandle_t xTimer )
{
		key[0].state=HAL_GPIO_ReadPin(LIGHTA4_GPIO_Port,LIGHTA4_Pin);
		key[1].state=HAL_GPIO_ReadPin(LIGHTA5_GPIO_Port,LIGHTA5_Pin);
		key[2].state=HAL_GPIO_ReadPin(LIGHT_GPIO_Port,LIGHT_Pin);
		for(uint8_t i=0;i<NUM_Lights;i++)
		{
			switch (key[i].step)
			{
				case 0:
					if(key[i].state)//按键按下
					{
						key[i].step=1;
					}
					break;
				case 1:
					if(key[i].state)//按键还是按下状态
					{
						key[i].step=2;
					}else//按键已经松开
					{
						key[i].step=0;
					}
					break;
				case 2:
					if(!key[i].state)//按键松开
					{
						key[i].flag = 1;
						key[i].step=0;
					}
					break;
			}
		}
}

uint8_t xtimer = 0;

/* 定时利用PID进行调速 */
void SpeedSetTimerFun( TimerHandle_t xTimer )
{
	xtimer++;
	if(xtimer == 10)//电机二PID
	{
		xtimer = 0;
		motor2.speed = motor2.timers;
		if(motor2.TPID.setpoint == 0)
		{
			Motor_SetSpeed(2,0);
		}
		else
		{
			Motor_SetSpeed(2, (int)(PID_Compute(&motor2.TPID,motor2.speed))+motor2.CompSpeed);
		}
		motor2.timers = 0;


		motor3.speed = motor3.timers;
		if(motor3.TPID.setpoint == 0)
		{
			Motor_SetSpeed(3,0);
		}
		else
		{
			Motor_SetSpeed(3, (int)(PID_Compute(&motor3.TPID,motor3.speed))+motor3.CompSpeed);
		}
		motor3.timers = 0;
	}

	motor1.speed = motor1.timers;
	if(motor1.TPID.setpoint == 0)
	{
		Motor_SetSpeed(1,0);
	}
	else
	{
		Motor_SetSpeed(1, (int)(PID_Compute(&motor1.TPID,motor1.speed))+motor1.CompSpeed);
	}
	motor1.timers = 0;

}

void Motor_SetCompSpeed(MOTOR *motor,uint16_t speed)
{
	motor->CompSpeed = speed;
}

void PID_setMotorPoint(MOTOR *motor,float speed)
{

		if(speed < 0)//设置速度补偿
		{
			motor->CompSpeed = motor->_SPEED * -1;
		}
		else
		{

			motor->CompSpeed = motor->_SPEED;
		}
		motor->TPID.setpoint = speed;

}


void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
	if(GPIO_Pin == MOTOR1_ENCODEA_EXTI_PIN)
	{
		if(HAL_GPIO_ReadPin(MOTOR1_ENCODEB_PORT,MOTOR1_ENCODEB_PIN) == GPIO_PIN_SET)
		{
			motor1.timers++;
			motor1.state = true;
		}
		else
		{
			motor1.timers--;
			motor1.state = false;
		}
	}
	else if(GPIO_Pin == MOTOR2_ENCODEA_EXTI_PIN)
	{

        if(HAL_GPIO_ReadPin(MOTOR2_ENCODEB_PORT, MOTOR2_ENCODEB_PIN) == GPIO_PIN_SET)
        {
			motor2.timers++;
            motor2.state = true;
        }
        else
        {
			motor2.timers--;
            motor2.state = false;
        }
	}
	else if(GPIO_Pin == MOTOR3_ENCODEA_EXTI_PIN)
	{

        if(HAL_GPIO_ReadPin(MOTOR3_ENCODEB_PORT, MOTOR3_ENCODEB_PIN) == GPIO_PIN_SET)
        {
			motor3.timers--;
            motor3.state = false;
        }
        else
        {
			motor3.timers++;
            motor3.state = true;
        }
	}
	else if(GPIO_Pin == MOTOR4_ENCODEA_EXTI_PIN)
	{
        if(HAL_GPIO_ReadPin(MOTOR4_ENCODEB_PORT, MOTOR4_ENCODEB_PIN) == GPIO_PIN_SET)
        {
			motor4.timers--;
            motor4.state = true;
        }
        else
        {
			motor4.timers++;
            motor4.state = false;
        }
	}
}

