#include "sdkconfig.h"
#include "nvs_flash.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_http_client.h"
#include "esp_log.h"
#include "esp_sleep.h"
#include "esp32/rom/uart.h"
#include "freertos/semphr.h"

#include "./inc/global.h"
#include "./inc/wifi.h"
#include "./inc/mqtt.h"
#include "./inc/nvs.h"
#include "./inc/seguranca.h"
#include "./inc/config_pinos.h"

#define MODO_BATERIA CONFIG_ESP_MODO_BATERIA

SemaphoreHandle_t conexaoWifiSemaphore;
SemaphoreHandle_t conexaoMQTTSemaphore;

char atributos[50];

void handleLowPower() {
  vTaskDelay(4000 / portTICK_PERIOD_MS);

  ESP_LOGI("Sleep", "Indo dormir...");
  uart_tx_wait_idle(CONFIG_ESP_CONSOLE_UART_NUM);
  esp_light_sleep_start();
}

void conectadoWifi(void *params) {
  while (true) {
    if (xSemaphoreTake(conexaoWifiSemaphore, portMAX_DELAY)) {
      mqtt_start();
      
      while (true) {
        if (xSemaphoreTake(conexaoMQTTSemaphore, portMAX_DELAY)) {
          while (true) {
            if (MODO_BATERIA == true) {
              handleLowPower();
              ESP_LOGI("Sleep", "Acordei!");
            }

            sprintf(atributos, "{\"sistemaAtivado\": %ld}", sistemaAtivado);
            grava_valor_nvs(sistemaAtivado);
            mqtt_envia_mensagem(1, "v1/devices/me/attributes", atributos);
            mqtt_envia_mensagem(2, "casa/automatica/seguranca", atributos);
            vTaskDelay(1000 / portTICK_PERIOD_MS);
          }
        }
      }
    }
  }
}

void app_main(void) {
  esp_err_t ret = nvs_flash_init();
  if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
    ESP_ERROR_CHECK(nvs_flash_erase());
    ret = nvs_flash_init();
  }
  ESP_ERROR_CHECK(ret);

  conexaoWifiSemaphore = xSemaphoreCreateBinary();
  conexaoMQTTSemaphore = xSemaphoreCreateBinary();
  wifi_start();

  if (MODO_BATERIA == true) {
    esp_sleep_enable_timer_wakeup(10 * 1000000);
  }

  config_pinos();

  xTaskCreate(&conectadoWifi, "Conexão ao MQTT", 4096, NULL, 1, NULL);
  xTaskCreate(&sistemaDeSeguranca, "Sistema de Segurança", 4096, NULL, 1, NULL);
}
