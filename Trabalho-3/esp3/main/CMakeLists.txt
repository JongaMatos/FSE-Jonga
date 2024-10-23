set(EXTRA_COMPONENT_DIRS ../components/ssd1306)
idf_component_register(SRCS "adc_module.c" "gpio_setup.c" "ntc.c" "wifi.c" "mqtt.c" "main.c"
                    INCLUDE_DIRS ".")