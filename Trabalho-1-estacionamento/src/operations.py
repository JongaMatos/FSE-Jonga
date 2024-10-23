###################################################
# operations.py                                   #
###################################################

import RPi.GPIO as GPIO
import time
import uuid
from datetime import datetime


def registra_entrada():
    identificador = str(uuid.uuid4())
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Carro entrou: ID={identificador}, Data/Hora={data_hora}")
    # Add codigo para jogar id no server
    return identificador


def opera_cancela(sensor1, sensor2, motorCancela, contadorDict, contadorAndar, direcao):
    while True:
        if (GPIO.input(sensor1) == GPIO.HIGH):
            if (GPIO.input(motorCancela) == GPIO.LOW):
                identificador = registra_entrada()
                GPIO.output(motorCancela, GPIO.HIGH)
                print("Abrindo a cancela")
        if (GPIO.input(sensor2) == GPIO.HIGH):
            if (GPIO.input(motorCancela) == GPIO.HIGH):
                GPIO.output(motorCancela, GPIO.LOW)
                print("Fechando a cancela")
                if (direcao == 'in'):
                    contadorDict[contadorAndar] += 1
                if (direcao == 'out'):
                    contadorDict[contadorAndar] -= 1


def observa_passagem(sensor1, sensor2, contadorDict, contadorAndarBaixo, contadorAndarAlto):
    ultimoSensor = 0
    while True:
        if (GPIO.input(sensor1)):
            if (ultimoSensor == 2):
                print("Descendo")
                contadorDict[contadorAndarBaixo] = +1
                contadorDict[contadorAndarAlto] = -1
                ultimoSensor = 0
                time.sleep(0.3)

            else:
                ultimoSensor = 1
        if (GPIO.input(sensor2)):
            if (ultimoSensor == 1):
                print("Subindo")
                contadorDict[contadorAndarAlto] += 1
                contadorDict[contadorAndarBaixo] -= 1
                ultimoSensor = 0
                time.sleep(0.3)

            else:
                ultimoSensor = 2


def aciona_lotado(estadoVagas, sinal, andar, forceStatus='none'):
    while True:
        ultima_lotacao = GPIO.input(sinal)
        lotacao_atual = all(x == 1 for x in estadoVagas[0:])
        if (forceStatus == 'Open'):
            lotacao_atual = False
        if (forceStatus == "Close"):
            lotacao_atual = True
        # print(f"Estado {andar}:{estadoVagas}\n")
        if (lotacao_atual != ultima_lotacao):
            GPIO.output(sinal, lotacao_atual)
            ultima_lotacao = lotacao_atual
            if (lotacao_atual):
                print(f"{andar} está lotado")
            else:
                print(f"{andar} possui vagas")

        time.sleep(1)


def aciona_lotado_terreo(estadoVagas, sinalTerreo, sinal1Andar, sinal2Andar, forceStatus='none'):

    while True:
        lotacaoTerreo = GPIO.input(sinalTerreo)

        if (forceStatus == "Open"):
            GPIO.output(sinalTerreo, GPIO.LOW)
        elif (forceStatus == "Closed"):
            GPIO.output(sinalTerreo, GPIO.HIGH)
        else:
            lotacao1Andar = GPIO.input(sinal1Andar)
            lotacao2Andar = GPIO.input(sinal2Andar)
            if (not lotacao1Andar or not lotacao2Andar):
                if (lotacaoTerreo):
                    GPIO.output(sinalTerreo, GPIO.LOW)
            else:
                lotacao_Atual_Terreo = all(x == 1 for x in estadoVagas[0:])
                if (lotacao_Atual_Terreo != lotacaoTerreo):
                    GPIO.output(sinalTerreo, lotacao_Atual_Terreo)

        time.sleep(0.5)


def int_to_bin_array(n):
    binVal = bin(n)[2:].zfill(3)
    return [int(binVal[0]), int(binVal[1]), int(binVal[2])]


def verifica_vagas(endereço1, endereço2, endereço3, sensor, estadoVagas, sinalLotacao, letra):

    while True:
        # novosEstadosVagas=[]
        for i in range(8):
            indiceVaga = int_to_bin_array(i)

            GPIO.output(endereço1, indiceVaga[0])
            GPIO.output(endereço2, indiceVaga[1])
            GPIO.output(endereço3, indiceVaga[2])
            time.sleep(0.3)
            vaga_atual = GPIO.input(sensor)
            if (vaga_atual != estadoVagas[i]):
                estadoVagas[i] = vaga_atual
                if (estadoVagas[i] == GPIO.HIGH):
                    print(f"Ocupou a vaga {letra}{i+1}")
                else:
                    print(f"Liberou a vaga {letra}{i+1}")