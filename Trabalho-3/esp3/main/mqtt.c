#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "esp_system.h"
#include "esp_event.h"
#include "esp_netif.h"

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "freertos/queue.h"

#include "lwip/sockets.h"
#include "lwip/dns.h"
#include "lwip/netdb.h"

#include "esp_log.h"
#include "mqtt_client.h"

#include "mqtt.h"
#include "global.h"

#define TAG "MQTT"

extern SemaphoreHandle_t conexaoMQTTSemaphore;
esp_mqtt_client_handle_t client1;
esp_mqtt_client_handle_t client2;
// int led_status=-1;

static void log_error_if_nonzero(const char *message, int error_code)
{
    if (error_code != 0)
    {
        ESP_LOGE(TAG, "Last error %s: 0x%x", message, error_code);
    }
}

static void mqtt_event_handler(void *handler_args, esp_event_base_t base, int32_t event_id, void *event_data)
{
    ESP_LOGD(TAG, "Event dispatched from event loop base=%s, event_id=%d", base, (int)event_id);
    esp_mqtt_event_handle_t event = event_data;
    esp_mqtt_client_handle_t client = event->client;
    int msg_id;
    switch ((esp_mqtt_event_id_t)event_id)
    {
    case MQTT_EVENT_CONNECTED:
        ESP_LOGI(TAG, "MQTT_EVENT_CONNECTED");
        xSemaphoreGive(conexaoMQTTSemaphore);
        msg_id = esp_mqtt_client_subscribe(client, "v1/devices/me/rpc/request/+", 0);
        msg_id = esp_mqtt_client_subscribe(client, "casa/automatica/+", 0);
        break;
    case MQTT_EVENT_DISCONNECTED:
        ESP_LOGI(TAG, "MQTT_EVENT_DISCONNECTED");
        break;

    case MQTT_EVENT_SUBSCRIBED:
        ESP_LOGI(TAG, "MQTT_EVENT_SUBSCRIBED, msg_id=%d", event->msg_id);
        msg_id = esp_mqtt_client_publish(client, "/topic/qos0", "data", 0, 0, 0);
        ESP_LOGI(TAG, "sent publish successful, msg_id=%d", msg_id);
        break;
    case MQTT_EVENT_UNSUBSCRIBED:
        ESP_LOGI(TAG, "MQTT_EVENT_UNSUBSCRIBED, msg_id=%d", event->msg_id);
        break;
    case MQTT_EVENT_PUBLISHED:
        ESP_LOGI(TAG, "MQTT_EVENT_PUBLISHED, msg_id=%d", event->msg_id);
        break;
    case MQTT_EVENT_DATA:
        ESP_LOGI(TAG, "MQTT_EVENT_DATA");
        printf("TOPIC=%.*s\r\n", event->topic_len, event->topic);
        printf("DATA=%.*s\r\n", event->data_len, event->data);
        if (strcmp(event->topic,"casa/automatica/luz"))
        {

            if (event->data[15] == '1')
            {
                led_status = 1;
            }
            else if (event->data[15] == '0')
            {
                led_status = 0;
            }
        }
        if (strcmp(event->topic,"casa/automatica/seguranca"))
        {
            if (event->data[19] == '1')
            {
                sistemaAtivado = 1;
            }
            else if (event->data[19] == '0')
            {
                sistemaAtivado = 0;
            }
        }
        break;
    case MQTT_EVENT_ERROR:
        ESP_LOGI(TAG, "MQTT_EVENT_ERROR");
        if (event->error_handle->error_type == MQTT_ERROR_TYPE_TCP_TRANSPORT)
        {
            log_error_if_nonzero("reported from esp-tls", event->error_handle->esp_tls_last_esp_err);
            log_error_if_nonzero("reported from tls stack", event->error_handle->esp_tls_stack_err);
            log_error_if_nonzero("captured as transport's socket errno", event->error_handle->esp_transport_sock_errno);
            ESP_LOGI(TAG, "Last errno string (%s)", strerror(event->error_handle->esp_transport_sock_errno));
        }
        break;
    default:
        ESP_LOGI(TAG, "Other event id:%d", event->event_id);
        break;
    }
}

void mqtt_start()
{
    esp_mqtt_client_config_t mqtt_config1 = {
        .broker.address.uri = "mqtt://164.41.98.25",
        .credentials.username = "unRNm9I8SbPCVUibjKQF",
    };

    esp_mqtt_client_config_t mqtt_config2 = {
        .broker.address.uri = "mqtt://164.41.98.24",
        .credentials.username = "unRNm9I8SbPCVUibjKQF",
    };

    client1 = esp_mqtt_client_init(&mqtt_config1);
    esp_mqtt_client_register_event(client1, ESP_EVENT_ANY_ID, mqtt_event_handler, NULL);
    esp_mqtt_client_start(client1);

    client2 = esp_mqtt_client_init(&mqtt_config2);
    esp_mqtt_client_register_event(client2, ESP_EVENT_ANY_ID, mqtt_event_handler, NULL);
    esp_mqtt_client_start(client2);
}

void mqtt_envia_mensagem(int clientid, char *topico, char *mensagem)
{
    int message_id;
    if (clientid == 1)
        message_id = esp_mqtt_client_publish(client1, topico, mensagem, 0, 1, 0);
    else
        message_id = esp_mqtt_client_publish(client2, topico, mensagem, 0, 1, 0);

    ESP_LOGI(TAG, "Mesnagem enviada, ID: %d", message_id);
}