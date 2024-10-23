#ifndef MQTT_H
#define MQTT_H

// int led_status;

void mqtt_start();

void mqtt_envia_mensagem(int client,char * topico, char * mensagem);

#endif