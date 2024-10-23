#ifndef MQTT_H
#define MQTT_H

void mqtt_start();

void mqtt_envia_mensagem(int id, char * topico, char * mensagem);

#endif