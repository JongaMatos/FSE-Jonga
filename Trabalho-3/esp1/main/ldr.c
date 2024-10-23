#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "esp_log.h"
#include "esp_event.h"
#include "freertos/semphr.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "sdkconfig.h"
#include "driver/adc.h"
#include "driver/ledc.h"
#include "pthread.h"
#include "esp_pthread.h"

#include "ldr.h"
#include "mqtt.h"
#include "nvs_setup.h"
#include "gpio_setup.h"
#include "adc_module.h"

// Média Móvel das Leituras
int readings[NUM_READINGS]; // Array para armazenar leituras to store readings
int readIndex = 0;
float total = 0;
float average = 0;
// Valores ADC e de Luminosidade
float ldr_lux = 0;
float adc_value = 0.0048828125;

bool has_ldr_sensor() {
    return SENSOR_LDR > 0;
}

void ldr_setup() {
    if (!has_ldr_sensor())
        return;

    // Configura GPIO com ADC
    adc_init(ADC_UNIT_1);

    // Habilita entrada PullUp para o Resistor LDR diminuir intensidade na incidência de Luminosidade
    pinMode(SENSOR_LDR, GPIO_ANALOG);

    // Configurando LED
    esp_rom_gpio_pad_select_gpio(LED);
    gpio_set_direction(LED, GPIO_MODE_OUTPUT);

}

void ldr_loop() {
    if (!has_ldr_sensor())
        return;

    int ldr_value = 0;

    while (true) {
        ldr_value = analogRead(SENSOR_LDR);
        // Conversão do valor analógico para valor lux
        ldr_lux = (250.000000/(adc_value*ldr_value))-50.000000;
        printf("Valor LUX LDR: %f lux\n", ldr_lux);
        
        vTaskDelay(500 / portTICK_PERIOD_MS); // Verifica a cada 500 milisegundos

        // Desloca as leituras anteriores e adicione a nova
        total -= readings[readIndex];
        readings[readIndex] = ldr_lux;
        total += readings[readIndex];
        readIndex = (readIndex + 1) % NUM_READINGS;

        // Calcula a média
        average = total / NUM_READINGS;
        printf("Valor average: %d lux\n", (int) average);

        // Verifica se a luminosidade está abaixo do limiar
        if (average > THRESHOLD) {
            // Pouca luz (valor negativo do lux) -> Acende o LED
            digitalWrite(LED, 1);
            // Grava estado do LED no NVS
            grava_valor_nvs(1);
        } else {
            // Muita luz (valor positivo do lux) -> Apaga o LED
            digitalWrite(LED, 0);
            // Grava estado do LED no NVS
            grava_valor_nvs(0);
        }

        vTaskDelay(1000 / portTICK_PERIOD_MS); // Verifica a cada 1 segundo
    }
}