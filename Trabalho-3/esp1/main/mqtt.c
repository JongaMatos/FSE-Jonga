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
#include "driver/gpio.h"

#include "lwip/sockets.h"
#include "lwip/dns.h"
#include "lwip/netdb.h"
#include "cJSON.h"
#include "ldr.h"
#include "gpio_setup.h"
#include "esp_log.h"
#include "mqtt_client.h"
#include "mqtt.h"

#define TAG "MQTT"

extern SemaphoreHandle_t conexaoMQTTSemaphore;
esp_mqtt_client_handle_t client1;
esp_mqtt_client_handle_t client2;


uint16_t request_id = 0;

void handle_mqtt_request(const char* message, uint16_t request_id) {
    // Tenta converter a mensagem MQTT recebida para um objeto JSON
    cJSON *root = cJSON_Parse(message);
    if (root == NULL) {
        // Se falhar na conversão, libera a memória e retorna
        cJSON_Delete(root);
        return;
    }

    // Extrai o método e parâmetros do JSON
    cJSON *method = cJSON_GetObjectItemCaseSensitive(root, "method");
    cJSON *params = cJSON_GetObjectItemCaseSensitive(root, "params");

    // Verifica se o método é uma string e se os parâmetros são um objeto JSON
    if (cJSON_IsString(method) && cJSON_IsObject(params)) {
         // Verifica se o método é "control_lighting" ou "check_light_status"
        if (strcmp(method->valuestring, "check_led_status") == 0 || strcmp(method->valuestring, "control_lighting") == 0) {

            int led_status = gpio_get_level(LED);

            // Prepara o tópico de resposta
            char response_topic[50];
            sprintf(response_topic, "v1/devices/me/rpc/response/%d", request_id);
            
            // Cria a resposta JSON
            cJSON *response = cJSON_CreateObject();
            cJSON_AddItemToObject(response, "light_status", cJSON_CreateString(led_status ? "on" : "off"));
            // Envia a resposta para o tópico RPC
            esp_mqtt_client_publish(client1, response_topic, cJSON_PrintUnformatted(response), 0, 0, 0);

            // Envia também como um atributo para o dashboard para atualizar o widget LED Indicator
            mqtt_envia_mensagem(1,"v1/devices/me/attributes", cJSON_PrintUnformatted(response));

            // Opcional: Envia a confirmação de que o comando foi recebido
            // char response_topic[50];
            // sprintf(response_topic, "v1/devices/me/rpc/response/%d", request_id);
            // esp_mqtt_client_publish(client, response_topic, "{\"status\": \"success\"}", 0, 0, 0);

            cJSON_Delete(response);
        }
    }

    // Libera a memória do objeto JSON
    cJSON_Delete(root);
}

static void log_error_if_nonzero(const char *message, int error_code)
{
    if (error_code != 0) {
        ESP_LOGE(TAG, "Last error %s: 0x%x", message, error_code);
    }
}

static void mqtt_event_handler(void *handler_args, esp_event_base_t base, int32_t event_id, void *event_data)
{
    ESP_LOGD(TAG, "Event dispatched from event loop base=%s, event_id=%d", base, (int) event_id);
    esp_mqtt_event_handle_t event = event_data;
    esp_mqtt_client_handle_t client = event->client;
    int msg_id;
    switch ((esp_mqtt_event_id_t)event_id) {
    case MQTT_EVENT_CONNECTED:
        ESP_LOGI(TAG, "MQTT_EVENT_CONNECTED");
        xSemaphoreGive(conexaoMQTTSemaphore);
        // msg_id = esp_mqtt_client_subscribe(client, "dispositivos/#", 0);
        // Subscribe correto para se inscrever no Broker do ThingsBoard, seguindo a API do MQTT Device
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

        // Lida com a requisição vindo do dashboard no ThingsBoards via MQTT
        // const char *data = event->data;
        // handle_mqtt_request(data, request_id);
        break;
    case MQTT_EVENT_ERROR:
        ESP_LOGI(TAG, "MQTT_EVENT_ERROR");
        if (event->error_handle->error_type == MQTT_ERROR_TYPE_TCP_TRANSPORT) {
            log_error_if_nonzero("reported from esp-tls", event->error_handle->esp_tls_last_esp_err);
            log_error_if_nonzero("reported from tls stack", event->error_handle->esp_tls_stack_err);
            log_error_if_nonzero("captured as transport's socket errno",  event->error_handle->esp_transport_sock_errno);
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
        .credentials.username = "FibaWfKejqaOUxVBdBzC",
    };
    client1 = esp_mqtt_client_init(&mqtt_config1);
    esp_mqtt_client_register_event(client1, ESP_EVENT_ANY_ID, mqtt_event_handler, NULL);
    esp_mqtt_client_start(client1);

    esp_mqtt_client_config_t mqtt_config2 = {
        .broker.address.uri = "mqtt://164.41.98.24", 
        .credentials.username = "FibaWfKejqaOUxVBdBzC",
    };
    client2 = esp_mqtt_client_init(&mqtt_config2);
    esp_mqtt_client_register_event(client2, ESP_EVENT_ANY_ID, mqtt_event_handler, NULL);
    esp_mqtt_client_start(client2);

}

void mqtt_envia_mensagem(int id, char * topico, char * mensagem)
{
    int message_id;
    if(id==1)
    message_id = esp_mqtt_client_publish(client1, topico, mensagem, 0, 1, 0);
    else
    message_id = esp_mqtt_client_publish(client2, topico, mensagem, 0, 1, 0);

    ESP_LOGI(TAG, "Mensagem enviada, ID: %d", message_id);
}