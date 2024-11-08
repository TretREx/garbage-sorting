/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2024 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32f1xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define MOTOR_Pin GPIO_PIN_13
#define MOTOR_GPIO_Port GPIOC
#define MOTORC14_Pin GPIO_PIN_14
#define MOTORC14_GPIO_Port GPIOC
#define LIGHT_Pin GPIO_PIN_15
#define LIGHT_GPIO_Port GPIOC
#define TIM_MOTOR_Pin GPIO_PIN_0
#define TIM_MOTOR_GPIO_Port GPIOA
#define TIM_MOTORA1_Pin GPIO_PIN_1
#define TIM_MOTORA1_GPIO_Port GPIOA
#define TIM_MOTORA2_Pin GPIO_PIN_2
#define TIM_MOTORA2_GPIO_Port GPIOA
#define TIM_MOTORA3_Pin GPIO_PIN_3
#define TIM_MOTORA3_GPIO_Port GPIOA
#define LIGHTA4_Pin GPIO_PIN_4
#define LIGHTA4_GPIO_Port GPIOA
#define LIGHTA5_Pin GPIO_PIN_5
#define LIGHTA5_GPIO_Port GPIOA
#define TIM_SERVO_Pin GPIO_PIN_6
#define TIM_SERVO_GPIO_Port GPIOA
#define TIM_SERVOA7_Pin GPIO_PIN_7
#define TIM_SERVOA7_GPIO_Port GPIOA
#define TIM_SERVOB0_Pin GPIO_PIN_0
#define TIM_SERVOB0_GPIO_Port GPIOB
#define TIM_SERVOB1_Pin GPIO_PIN_1
#define TIM_SERVOB1_GPIO_Port GPIOB
#define MOTORB3_Pin GPIO_PIN_3
#define MOTORB3_GPIO_Port GPIOB
#define MOTORB4_Pin GPIO_PIN_4
#define MOTORB4_GPIO_Port GPIOB
#define MOTORB5_Pin GPIO_PIN_5
#define MOTORB5_GPIO_Port GPIOB
#define MOTORB6_Pin GPIO_PIN_6
#define MOTORB6_GPIO_Port GPIOB
#define MOTORB7_Pin GPIO_PIN_7
#define MOTORB7_GPIO_Port GPIOB
#define MOTORB8_Pin GPIO_PIN_8
#define MOTORB8_GPIO_Port GPIOB

/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
