#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "esp_log.h"
#include "driver/gpio.h"

#include "../inc/config_pinos.h"

void config_pinos() {
    esp_rom_gpio_pad_select_gpio(LED_B);
    esp_rom_gpio_pad_select_gpio(LED_R);
    esp_rom_gpio_pad_select_gpio(LED_G);
    esp_rom_gpio_pad_select_gpio(LED_PLACA);
    esp_rom_gpio_pad_select_gpio(BUZZER);
    esp_rom_gpio_pad_select_gpio(DIGITAL_SOUND);

    gpio_set_direction(LED_B, GPIO_MODE_OUTPUT);
    gpio_set_direction(LED_R, GPIO_MODE_OUTPUT);
    gpio_set_direction(LED_G, GPIO_MODE_OUTPUT);
    gpio_set_direction(LED_PLACA, GPIO_MODE_OUTPUT);
    gpio_set_direction(BUZZER, GPIO_MODE_OUTPUT);

    gpio_set_direction(DIGITAL_SOUND, GPIO_MODE_INPUT);

    gpio_set_level(LED_B, 1);
    gpio_set_level(LED_R, 1);
    gpio_set_level(LED_G, 1);
    gpio_set_level(LED_PLACA, 0);
    gpio_set_level(BUZZER, 0);
}