from threading import Thread
from time import sleep

from gpio import GPIOController
from utils import get_temperatura
import comandos


def atualiza_temperatura():
    ultima_temperatura_1 = 0
    ultima_temperatura_2 = 0
    while not comandos.stop:
        temperatura_1 = get_temperatura(1)
        temperatura_2 = get_temperatura(2)
        if temperatura_1 != ultima_temperatura_1:
            ultima_temperatura_1 = temperatura_1
            comandos.envia_temperatura(1, temperatura_1)

        if temperatura_2 != ultima_temperatura_2:
            ultima_temperatura_2 = temperatura_2
            comandos.envia_temperatura(2, temperatura_2)

        sleep(1)

    return





def atualiza_registradores(endereco,gpio):
    ultimo_valor = {}
    while True:
        valor = comandos.apura_registradores(endereco)
        if ultimo_valor != valor:
            ultimo_valor = valor
            gpio.update(ultimo_valor)

        sleep(0.1)



try:
    thread_envio = Thread(target=comandos.uart.envia_array)
    thread_envio.daemon = True
    thread_envio.start()
    thread_temperatura = Thread(target=atualiza_temperatura)
    thread_temperatura.daemon = True
    thread_temperatura.start()

    gpio1 = GPIOController()
    gpio2 = GPIOController()

    
    gpio1.calibra()
    gpio2.calibra()


    

    thread_registradores1 = Thread(target=atualiza_registradores,args=(0x00,gpio1))
    thread_registradores2 = Thread(target=atualiza_registradores,args=(0xA0,gpio2))
    
    thread_registradores1.daemon = True
    thread_registradores2.daemon = True

    thread_registradores1.start()
    thread_registradores2.start()

    thread_registradores1.join()
    thread_registradores2.join()
    thread_temperatura.join()
    thread_envio.join()
    thread_temperatura.join()
except KeyboardInterrupt:

    gpio1.encerra()
    gpio2.encerra()

finally:
    comandos.encerra()
