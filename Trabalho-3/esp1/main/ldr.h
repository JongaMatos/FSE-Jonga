#ifndef LDR_H
#define LDR_H
#define SENSOR_LDR ADC_CHANNEL_6 // GPIO34
#define LED 2
#define THRESHOLD 0
#define NUM_READINGS 5

bool has_ldr_sensor();
void ldr_setup();
void ldr_loop();

#endif