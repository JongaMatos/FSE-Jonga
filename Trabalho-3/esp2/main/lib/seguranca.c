#include <stdint.h>
#include "esp_log.h"
#include "esp_event.h"
#include "driver/gpio.h"

#include "../inc/global.h"
#include "../inc/nvs.h"
#include "../inc/config_pinos.h"

int alerts = 0;
int32_t sistemaAtivado = 0;

void sistemaDeSeguranca(void *params) {
    sistemaAtivado = le_valor_nvs();
    if (sistemaAtivado == -1)
        sistemaAtivado = 1;

    int sensor = 0;
    int estado = 1;

    while (true) {
        if (sistemaAtivado == 1) {
            sensor = gpio_get_level(DIGITAL_SOUND);
            ESP_LOGI("Sensor", "Sensor Output: %d - Alarmes: %d", sensor, alerts);

            if (sensor == 1)
                alerts++;

            while (alerts >= 3) {
                estado = 1 - estado;
                gpio_set_level(LED_PLACA, 1);
                gpio_set_level(BUZZER, (1 - estado));
                gpio_set_level(LED_R, (estado));
                gpio_set_level(LED_B, (1 - estado));
                vTaskDelay(200 / portTICK_PERIOD_MS);
            }

            estado = 1 - estado;
            gpio_set_level(LED_PLACA, estado);
            gpio_set_level(LED_R, 1);
            gpio_set_level(LED_B, 1);
            gpio_set_level(BUZZER, 0);
            vTaskDelay(200 / portTICK_PERIOD_MS);
        } else {
            gpio_set_level(LED_PLACA, 0);
            gpio_set_level(LED_R, 1);
            gpio_set_level(LED_B, 1);
            gpio_set_level(BUZZER, 0);
            vTaskDelay(200 / portTICK_PERIOD_MS);
        }
    }
}