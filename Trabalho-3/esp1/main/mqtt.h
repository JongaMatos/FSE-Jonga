#ifndef MQTT_H
#define MQTT_H

void mqtt_start();

void handle_mqtt_request(const char* message, uint16_t request_id);
void mqtt_envia_mensagem(int id, char * topico, char * mensagem);

#endif