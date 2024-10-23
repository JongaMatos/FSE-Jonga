#include <stdio.h>
#include <string.h>
#include "nvs_flash.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_http_client.h"
#include "esp_log.h"
#include "freertos/semphr.h"

#include "wifi.h"
#include "mqtt.h"
#include "ntc.h"
#include "global.h"

#define OLED_WIDTH 128
#define OLED_HEIGHT 64
#define OLED_SDA 21
#define OLED_SCL 22
#define OLED_INVERT false
#include "ssd1306.h"
#include "font8x8_basic.h"

void trataComunicacaoComServidor(void *params);
void conectadoWifi(void *params);

void oled_setup();
void set_oled_content();
void oled_update();

SemaphoreHandle_t conexaoWifiSemaphore;
SemaphoreHandle_t conexaoMQTTSemaphore;

float temperatura = 999;

SSD1306_t dev;

int line1_length = 0;
char line1_content[21];

int line2_length = 0;
char line2_content[21];

int line3_length = 0;
char line3_content[21];

int led_status = -1;
int sistemaAtivado = -1;

void app_main(void)
{
  // Inicializa o NVS
  esp_err_t ret = nvs_flash_init();
  if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND)
  {
    ESP_ERROR_CHECK(nvs_flash_erase());
    ret = nvs_flash_init();
  }
  ESP_ERROR_CHECK(ret);
  ntc_setup();
  temperatura = ntc_get_temperature();
  oled_setup();

  conexaoWifiSemaphore = xSemaphoreCreateBinary();
  conexaoMQTTSemaphore = xSemaphoreCreateBinary();
  wifi_start();

  xTaskCreate(&conectadoWifi, "Conexão ao MQTT", 4096, NULL, 1, NULL);
  xTaskCreate(&trataComunicacaoComServidor, "Comunicação com Broker", 4096, NULL, 1, NULL);

  while (true)
  {
    temperatura = ntc_get_temperature();
    oled_update();
    vTaskDelay(3000 / portTICK_PERIOD_MS);
  }
}

void conectadoWifi(void *params)
{
  while (true)
  {
    if (xSemaphoreTake(conexaoWifiSemaphore, portMAX_DELAY))
    {
      // Processamento Internet
      mqtt_start();
    }
  }
}

void trataComunicacaoComServidor(void *params)
{
  char mensagem[50];
  char json[50];
  if (xSemaphoreTake(conexaoMQTTSemaphore, portMAX_DELAY))
  {
    while (true)
    {
      sprintf(mensagem, "{\"temperatura\": %f}", temperatura);
      mqtt_envia_mensagem(1, "v1/devices/me/telemetry", mensagem);

      vTaskDelay(3000 / portTICK_PERIOD_MS);
    }
  }
}

#pragma region OLED functions

void oled_setup()
{

  i2c_master_init(&dev, OLED_SDA, OLED_SCL, 0);

  ssd1306_init(&dev, OLED_WIDTH, OLED_HEIGHT);
  ssd1306_clear_screen(&dev, false);
}

void oled_update()
{
  set_oled_content();
  // ssd1306_clear_screen(&dev, false);
  ssd1306_display_text(&dev, 0, line1_content, line1_length, false);
  ssd1306_display_text(&dev, 2, line2_content, line2_length, false);
  ssd1306_display_text(&dev, 4, line3_content, line3_length, false);
}

void set_oled_content()
{

  if (led_status == 0)
  {
    sprintf(line2_content, "LED: OFF          .");
    line2_length=17;
  }
  else if (led_status == 1)
  {
    sprintf(line2_content, "LED: ON          .");
    line2_length=17;

  }
  else
  {
    sprintf(line2_content, "LED: aguardando...");
    line2_length=17;

  }

  if (sistemaAtivado == 0)
  {
    sprintf(line3_content, "Seguranca: OFF");
    line3_length=17;
  }
  else if (sistemaAtivado == 1)
  {
    sprintf(line3_content, "Seguranca: ON");
    line3_length=17;

  }
  else
  {
    sprintf(line3_content, "Seguranca: ...");
    line3_length=17;

  }

  if (temperatura > 140 || temperatura < -40)
  {
    sprintf(line1_content, " ");
    line1_length = 0;
    return;
  }

  sprintf(line1_content, "Temp: %.2f C", temperatura);

  if (temperatura >= 100 || temperatura <= -10)
  {
    line1_length = 14;
    return;
  }

  if ((temperatura >= 10 && temperatura < 100) || (temperatura < 0 && temperatura >= -10))
  {
    line1_length = 13;
    return;
  }

  line1_length = 12;
  return;
}

#pragma endregion