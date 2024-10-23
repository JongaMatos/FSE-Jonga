##################################################
# gpio_utils.py                                  #
##################################################
import RPi.GPIO as GPIO


def reset_GPIOS():
    GPIO.setmode(GPIO.BCM)

    # Configurações para o andar térreo
    GPIO.setup(22, GPIO.OUT)  # ENDERECO_01
    GPIO.setup(26, GPIO.OUT)  # ENDERECO_02
    GPIO.setup(19, GPIO.OUT)  # ENDERECO_03
    GPIO.setup(18, GPIO.IN)   # SENSOR_DE_VAGA
    GPIO.setup(27, GPIO.OUT)  # SINAL_DE_LOTADO_FECHADO
    GPIO.setup(23, GPIO.IN)   # SENSOR_ABERTURA_CANCELA_ENTRADA
    GPIO.setup(24, GPIO.IN)   # SENSOR_FECHAMENTO_CANCELA_ENTRADA
    GPIO.setup(10, GPIO.OUT)  # MOTOR_CANCELA_ENTRADA
    GPIO.setup(25, GPIO.IN)   # SENSOR_ABERTURA_CANCELA_SAIDA
    GPIO.setup(12, GPIO.IN)   # SENSOR_FECHAMENTO_CANCELA_SAIDA
    GPIO.setup(17, GPIO.OUT)  # MOTOR_CANCELA_SAIDA

    # Configurações para o 1º andar
    GPIO.setup(13, GPIO.OUT)  # ENDERECO_01
    GPIO.setup(6, GPIO.OUT)   # ENDERECO_02
    GPIO.setup(5, GPIO.OUT)   # ENDERECO_03
    GPIO.setup(20, GPIO.IN)   # SENSOR_DE_VAGA
    GPIO.setup(8, GPIO.OUT)   # SINAL_DE_LOTADO_FECHADO
    GPIO.setup(16, GPIO.IN)   # SENSOR_DE_PASSAGEM_1
    GPIO.setup(21, GPIO.IN)   # SENSOR_DE_PASSAGEM_2

    # Configurações para o 2º andar
    GPIO.setup(9, GPIO.OUT)   # ENDERECO_01
    GPIO.setup(11, GPIO.OUT)  # ENDERECO_02
    GPIO.setup(15, GPIO.OUT)  # ENDERECO_03
    GPIO.setup(1, GPIO.IN)    # SENSOR_DE_VAGA
    GPIO.setup(14, GPIO.OUT)  # SINAL_DE_LOTADO_FECHADO
    GPIO.setup(0, GPIO.IN)    # SENSOR_DE_PASSAGEM_1
    GPIO.setup(7, GPIO.IN)    # SENSOR_DE_PASSAGEM_2

    # Confirmação de que os motores estão inicialmente desligados
    GPIO.output(10, GPIO.LOW)  # MOTOR_CANCELA_ENTRADA
    GPIO.output(17, GPIO.LOW)  # MOTOR_CANCELA_SAIDA



