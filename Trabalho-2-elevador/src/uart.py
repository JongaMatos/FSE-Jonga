
import serial
from time import sleep
import struct
from utils import get_crc

import uuid



class UART:

    def __init__(self):
        self.array=[]
        self.index=0
        self.__uart0_filestream = serial.Serial(
            port='/dev/ttyS0',
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
        )

        if self.__uart0_filestream == -1:
            print("Não foi possível iniciar a UART.\n")
            
        else:
            print("UART inicializada!\n")
            self.__block = False

    def envia_array(self):
        while not self.__block:
            if len(self.array)>self.index:
                atual=self.array[self.index]
                resposta = self.envia_recebe(atual['codigo'],atual['tamanho_resposta'])
                print(resposta)
                self.array[self.index]['resposta']=resposta
                self.index+=1
    
    def adiciona_elemento(self, codigo, tamanho_resposta):
        id=str(uuid.uuid4())
        self.array.append({'uuid':id,'codigo': codigo, "tamanho_resposta": tamanho_resposta, 'resposta':None})
        return id

    def __envia_comando(self, comando, *args):

        
        msg = bytes(comando)

        crc_calculado = get_crc(msg)
        msg +=  crc_calculado.to_bytes(2, 'little')
        self.__uart0_filestream.write(msg)

    def __recebe_resposta(self,size):

        if self.__uart0_filestream.in_waiting >= size:
            resposta = self.__uart0_filestream.read(size)

            if len(resposta) != size:
                print("Erro de comunicação")
                return None
            crc_calculado = get_crc(resposta[:-2])
            crc_recebido = struct.unpack('<H', resposta[-2:])[0]

            cod = resposta[1:2]
            if crc_calculado == crc_recebido:
                
                if cod == b'\x03': 
                    return {
                        "t_sobe":resposta[2],
                        "1_desce":resposta[3],
                        "1_sobe":resposta[4],
                        "2_desce":resposta[5],
                        "2_sobe":resposta[6],
                        "3_desce":resposta[7],
                        "b_emergencia":resposta[8],
                        "b_t":resposta[9],
                        "b_1":resposta[10],
                        "b_2":resposta[11],
                        "b_3":resposta[12],
                    }
                
                if cod == b'\x06':  # REG
                    return resposta[2]
                
                elif cod == b'\x16':  # PWM/Temperatura
                    return "ok"
                else:  #Encoder
                    info = resposta[3:7]
                    encoder = int.from_bytes(info, byteorder='little')
                    return encoder
            else:
                print("erro de crc")
                return None

    def envia_recebe(self, comando, size, *args,):

        if self.__block:
            return
        tentativas = 0
        self.__uart0_filestream.flushInput()
        while True:
            self.__envia_comando(comando, *args)
            sleep(0.05)
            resposta = self.__recebe_resposta(size)
            if resposta is not None:
                return resposta
            sleep(0.5)
            tentativas += 1

    def restart(self):
        self=self.__init__()

    def close(self):
        self.__uart0_filestream.close()
        self.__block=True
        print("UART finalizada")




    
