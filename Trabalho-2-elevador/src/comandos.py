from uart import UART
import struct
import RPi.GPIO as GPIO
from utils import get_temperatura
matricula=[2,2,3,8]

uart=UART()

ultima_temperatura_1=0
ultima_temperatura_2=0

stop = False

def find_index(uuid):
  for index, item in enumerate(uart.array):
      if item.get('uuid') == uuid:
        return index
  return None

def aguarda(uuid):
  index=find_index(uuid)

  while True:
    resposta=uart.array[index]['resposta']
    # print({'resposta':resposta})
    if resposta!=None:
      return resposta


def envia_temperatura(elevador, temperatura):
  uart.adiciona_elemento([0x01, 0x16, 0xD1, elevador-1,*struct.pack("<f", temperatura), *matricula], 5)
  return 

def apurar_encoder(idmotor):
    id = uart.adiciona_elemento([0x01, 0x23, 0xC1, idmotor] + matricula, 9)
    return aguarda(id) 

def apurar_pwm(idmotor, vel):
    uart.adiciona_elemento([0x01, 0x16, 0xC2, idmotor, *struct.pack("<i", vel)] + matricula, 5)
    return 

def apura_registradores(endereco):
    id = uart.adiciona_elemento([0x01, 0x03, endereco, 11 ] + matricula, 15)
    return aguarda(id) 
  
  
def escreve_registrador(endereco, valor=0):
    uart.adiciona_elemento([0x01, 0x06, endereco, 1, valor ] + matricula, 5)
    return 

def limpa_registrador(elevador:int, opcao ):
    if elevador>2 or elevador<1:
      return
    
    opcoes_e=['e', 'E']
    opcoes_t=['t', 'T', 0 , '0']
    opcoes_1=[1, '1']
    opcoes_2=[2, '2']
    opcoes_3=[3, '3']
    
    opcoes= opcoes_e + opcoes_t + opcoes_1 + opcoes_2 + opcoes_3
    
    if opcao not in opcoes:
      return
    
    enderecos={ 
                "t_sobe":0x00 + (elevador-1)*0xA0 ,  
                "1_desce":0x01 + (elevador-1)*0xA0,
                "1_sobe":0x02 + (elevador-1)*0xA01,
                "2_desce":0x03 + (elevador-1)*0xA0,
                "2_sobe":0x04 + (elevador-1)*0xA0,
                "3_desce":0x05 + (elevador-1)*0xA0,
                "b_emergencia":0x06 + (elevador-1)*0xA0,
                "b_t":0x07 + (elevador-1)*0xA0,
                "b_1":0x08 + (elevador-1)*0xA0,
                "b_2":0x09 + (elevador-1)*0xA0,
                "b_3":0x0A + (elevador-1)*0xA0,
              }
  
    if opcao in opcoes_e:
      escreve_registrador(enderecos['b_emergencia'])
      escreve_registrador(enderecos["t_sobe"])
      escreve_registrador(enderecos["b_t"])
      escreve_registrador(enderecos["1_desce"])
      escreve_registrador(enderecos["1_sobe"])
      escreve_registrador(enderecos["b_1"])
      escreve_registrador(enderecos["2_desce"])
      escreve_registrador(enderecos["2_sobe"])
      escreve_registrador(enderecos["b_2"])
      escreve_registrador(enderecos["3_desce"])
      escreve_registrador(enderecos["b_3"])
      return
    
    if opcao in opcoes_t:
      escreve_registrador(enderecos["t_sobe"])
      escreve_registrador(enderecos["b_t"])
      return

    if opcao in opcoes_1:
      escreve_registrador(enderecos["1_desce"])
      escreve_registrador(enderecos["1_sobe"])
      escreve_registrador(enderecos["b_1"])
      return
      
    if opcao in opcoes_2:
      escreve_registrador(enderecos["2_desce"])
      escreve_registrador(enderecos["2_sobe"])
      escreve_registrador(enderecos["b_2"])
      return
      
    if opcao in opcoes_3:
      escreve_registrador(enderecos["3_desce"])
      escreve_registrador(enderecos["b_3"])
      return
    



zeros=[0,0,0,0,0,0,0,0,0,0,0]

def encerra():
  stop=True
  
  uart.adiciona_elemento([0x01, 0x06, 0x00, 11, *zeros] + matricula, 15)
  uart.adiciona_elemento([0x01, 0x06, 0xA0, 11, *zeros] + matricula, 15)
  uart.close()
  
  GPIO.cleanup([20,21,12,18,23,24,25,19,26,13,17,27,22,6])
