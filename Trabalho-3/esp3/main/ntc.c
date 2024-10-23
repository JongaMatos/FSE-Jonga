#include "gpio_setup.h"
#include "adc_module.h"

#define ADC_CHANNEL ADC1_CHANNEL_0
#define ADC_WIDTH ADC_WIDTH_BIT_9
#define ADC_ATTEN ADC_ATTEN_DB_12

#define TEMP_SENSOR ADC_CHANNEL_0

void ntc_setup()
{
  adc_init(ADC_UNIT_1);
  pinMode(TEMP_SENSOR, GPIO_ANALOG);
}

float map(float value, float fromLow, float fromHigh, float toLow, float toHigh)
{
  if (fromHigh == fromLow)
  {
    // Handle division by zero case
    return toLow;
  }

  float mappedValue = toLow + (value - fromLow) * (toHigh - toLow) / (fromHigh - fromLow);
  return mappedValue;
}

float ntc_get_temperature()
{

  float analogValue = analogRead(TEMP_SENSOR);
  return map(analogValue, 0, 1023, 125, -40);
}