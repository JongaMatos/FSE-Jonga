#include <stdio.h>
#include <string.h>
#include "nvs.h"
#include "nvs_flash.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_http_client.h"
#include "esp_log.h"
#include "esp_sleep.h"
#include "freertos/semphr.h"
#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "cJSON.h"
#include "wifi.h"
#include "mqtt.h"
#include "gpio_setup.h"
#include "adc_module.h"
#include "nvs_setup.h"
#include "ldr.h"
#include "esp32/rom/uart.h"
#include <esp_sleep.h>

#define MODO_BATERIA CONFIG_MODO_BATERIA

SemaphoreHandle_t conexaoWifiSemaphore;
SemaphoreHandle_t conexaoMQTTSemaphore;

char json[50];

void mqtt_send_sleeping(int state){
  cJSON* response = cJSON_CreateObject();
  if (response == NULL){
      ESP_LOGE("LOW POWER", "Erro ao criar o json");
  }

  ESP_LOGI("Sleep", "Enviando modo da bateria para o dispositivo...");
  // Envia mensagem JSON com o estado da bateria, e qual o seu modo
  cJSON_AddItemToObject(response, "bateria", cJSON_CreateNumber(state));
  mqtt_envia_mensagem(1,"v1/devices/me/attributes", cJSON_Print(response));
  vTaskDelay(1000 / portTICK_PERIOD_MS);
}

void handleLowPower() {
  vTaskDelay(10000 / portTICK_PERIOD_MS); // Tempo até entrar em modo Low Power - 10 segundos
  mqtt_send_sleeping(1);
  ESP_LOGI("Sleep", "Indo dormir...");
  uart_tx_wait_idle(CONFIG_ESP_CONSOLE_UART_NUM);
  esp_light_sleep_start();
}

void conectadoWifi(void * params)
{
  while(true)
  {
    if(xSemaphoreTake(conexaoWifiSemaphore, portMAX_DELAY))
    {
      // Processamento Internet
      mqtt_start();

      // Verificações para ação com base na conexão MQTT
      while (true) {
          if (xSemaphoreTake(conexaoMQTTSemaphore, portMAX_DELAY)) {
            while (true) 
            {
              if (MODO_BATERIA == 1) {
                handleLowPower();
                mqtt_send_sleeping(0);
                ESP_LOGI("Sleep", "Acordei!");
              }

              int32_t valor_led_status = 0;
              int32_t led_status_valor_armazenado = le_valor_nvs(valor_led_status);
              printf("STATUS LED: (%ld) \n", led_status_valor_armazenado);

              // LED Ligado
              if (led_status_valor_armazenado == 1) {
                sprintf(json, "{\"led_status\": 1}");
                mqtt_envia_mensagem(1,"v1/devices/me/attributes", json);
                mqtt_envia_mensagem(2,"casa/automatica/luz", json);

              } else {
                // LED Desligado
                sprintf(json, "{\"led_status\": 0}");
                mqtt_envia_mensagem(1,"v1/devices/me/attributes", json);
                mqtt_envia_mensagem(2,"casa/automatica/luz", json);

              }
              vTaskDelay(1000 / portTICK_PERIOD_MS); // Ajuste o atraso conforme necessário
            }
          }
      }
    }
  }
}

void app_main(void)
{
  // Inicializa o NVS
  setup_nvs();

  conexaoWifiSemaphore = xSemaphoreCreateBinary();
  conexaoMQTTSemaphore = xSemaphoreCreateBinary();

  wifi_start();

  if (MODO_BATERIA == 1)
  {
    esp_sleep_enable_timer_wakeup(10 * 1000000); // acorda em 10 segundos
  }

  ldr_setup();
  
  xTaskCreate(&conectadoWifi,  "Conexão ao MQTT", 4096, NULL, 1, NULL);
  // Inicia a leitura do LDR e controle do LED
  xTaskCreate(&ldr_loop, "Leitura do LDR", 4096, NULL, 1, NULL);
  // xTaskCreate(&trataComunicacaoComServidor, "Comunicação com Broker", 4096, NULL, 1, NULL);
}