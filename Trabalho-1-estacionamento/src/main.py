import RPi.GPIO as GPIO
import time
import uuid
import socket
import threading
import requests
from flask import Flask, request, jsonify
from multiprocessing import Process, Manager
from datetime import datetime

from operations import *
from gpioUtils import *



###################################################
# central_server.py                               #
###################################################
app = Flask(__name__)

# Dados do estacionamento
estacionamento = {
    'total_carros': 0,
    'andares': {
        'terreo': {'carros': 0, 'vagas': 8, 'pagamentos': 0},
        'primeiro': {'carros': 0, 'vagas': 8, 'pagamentos': 0},
        'segundo': {'carros': 0, 'vagas': 8, 'pagamentos': 0}
    },
    'pagamentos_totais': 0,
    'status_lotado': False,
    'status_bloqueio_primeiro': False,
    'status_bloqueio_segundo': False
}

TAXA_POR_MINUTO = 0.10  # R$ 0,10 por minuto

# Endpoint para registrar entrada de carro


@app.route('/registro/entrada', methods=['POST'])
def registrar_entrada():
    dados = request.json
    andar = dados['andar']
    estacionamento['total_carros'] += 1
    estacionamento['andares'][andar]['carros'] += 1
    return jsonify({'status': 'entrada registrada'}), 200

# Endpoint para registrar saída de carro


@app.route('/registro/saida', methods=['POST'])
def registrar_saida():
    dados = request.json
    andar = dados['andar']
    valor_pago = dados['valor_pago']
    estacionamento['total_carros'] -= 1
    estacionamento['andares'][andar]['carros'] -= 1
    estacionamento['andares'][andar]['pagamentos'] += valor_pago
    estacionamento['pagamentos_totais'] += valor_pago
    return jsonify({'status': 'saida registrada'}), 200

# Função para interface do usuário


def interface_usuario():
    while True:
        print("\nEstado Atual do Estacionamento:")
        print(f"Total de carros: {estacionamento['total_carros']}")
        for andar, dados in estacionamento['andares'].items():
            print(
                f"{andar.capitalize()}: Carros: {dados['carros']}, Vagas disponíveis: {dados['vagas'] - dados['carros']}, Pagamentos: R${dados['pagamentos']:.2f}")
        print(f"Valor total pago: R${estacionamento['pagamentos_totais']:.2f}")
        print(
            f"Status Lotado: {'Sim' if estacionamento['status_lotado'] else 'Não'}")
        print(
            f"Bloqueio Primeiro Andar: {'Sim' if estacionamento['status_bloqueio_primeiro'] else 'Não'}")
        print(
            f"Bloqueio Segundo Andar: {'Sim' if estacionamento['status_bloqueio_segundo'] else 'Não'}")

        print("\nComandos disponíveis:")
        print("1: Fechar/abrir estacionamento")
        print("2: Bloquear/desbloquear Primeiro Andar")
        print("3: Bloquear/desbloquear Segundo Andar")
        print("4: Sair")

        comando = input("Digite o número do comando: ")

        if comando == '1':
            estacionamento['status_lotado'] = not estacionamento['status_lotado']
        elif comando == '2':
            estacionamento['status_bloqueio_primeiro'] = not estacionamento['status_bloqueio_primeiro']
        elif comando == '3':
            estacionamento['status_bloqueio_segundo'] = not estacionamento['status_bloqueio_segundo']
        elif comando == '4':
            break
        else:
            print("Comando inválido!")

# Função para tratar conexões dos clientes via socket


def handle_client_connection(client_socket):
    request = client_socket.recv(1024).decode()
    print(f'Received: {request}')

    # Parse da mensagem recebida
    if 'Ocupado' in request:
        slot_id = request.split()[-1]
        status = 'occupied'
    elif 'Livre' in request:
        slot_id = request.split()[-1]
        status = 'free'
    else:
        client_socket.close()
        return
    client_socket.close()

# Função para iniciar o servidor de sockets


def start_socket_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 12345))
    server.listen(5)
    print('Servidor central aguardando conexões...')
    while True:
        client_sock, address = server.accept()
        print(f"Conexão recebida de {address}")
        client_handler = threading.Thread(
            target=handle_client_connection,
            args=(client_sock,)
        )
        client_handler.start()


# Inicializa o servidor Flask e o servidor de sockets em threads diferentes




###################################################
# main.py                                         #
###################################################


if (__name__ == '__main__'):

    reset_GPIOS()

    # manager= Manager()
    contador_total = 0
    manager = Manager()
    contador_dict = manager.dict(
        {'contador_terreo': 0, 'contador_1_andar': 0, 'contador_2_andar': 0})

    # estado_vagas_terreo = [0, 0, 0, 0, 0, 0, 0, 0]
    estado_vagas_terreo = manager.Array('i', [0, 0, 0, 0, 0, 0, 0, 0])
    # estado_vagas_1_andar = [0, 0, 0, 0, 0, 0, 0, 0]
    estado_vagas_1_andar = manager.Array("i", [0, 0, 0, 0, 0, 0, 0, 0])
    # estado_vagas_2_andar = [0, 0, 0, 0, 0, 0, 0, 0]
    estado_vagas_2_andar = manager.Array("i", [0, 0, 0, 0, 0, 0, 0, 0])

    forceStatus1Andar = manager.Value('c', "none")
    forceStatus2Andar = manager.Value('c', "none")
    forceStatusEstacionamento = manager.Value('c', "none")

    # Cancelas entrada/saida
    cancela_entrada = Process(target=opera_cancela, args=(
        23, 24, 10, contador_dict, "contador_terreo", "in"))
    cancela_saida = Process(target=opera_cancela, args=(
        25, 12, 17, contador_dict, "contador_terreo", "out"))

    # Mudança de andar
    transicao_terreo_1 = Process(
        target=observa_passagem, args=(16, 21, contador_dict, "contador_terreo", "contador_1_andar"))
    transicao_1_2 = Process(
        target=observa_passagem, args=(0, 7, contador_dict, "contador_1_andar", "contador_2_andar"))

    # Ocupação das vagas
    vagas_terreo = Process(
        target=verifica_vagas, args=(22, 26, 19, 18, estado_vagas_terreo, 27, "T"))
    vagas_1_andar = Process(
        target=verifica_vagas, args=(13, 6, 5, 20, estado_vagas_1_andar, 8, "A"))
    vagas_2_andar = Process(
        target=verifica_vagas, args=(9, 11, 15, 1, estado_vagas_2_andar, 14, "B"))

    # Sinal de lotado
    lotacao_terreo = Process(
        target=aciona_lotado_terreo, args=(estado_vagas_terreo, 27, 8, 14, forceStatusEstacionamento))

    lotacao_1_andar = Process(
        target=aciona_lotado, args=(estado_vagas_1_andar, 8, "Primeiro andar", forceStatus1Andar))

    lotacao_2_andar = Process(
        target=aciona_lotado, args=(estado_vagas_2_andar, 14, "Segundo andar", forceStatus2Andar))

    # Start

    cancela_entrada.start()
    cancela_saida.start()

    transicao_terreo_1.start()
    transicao_1_2.start()

    vagas_terreo.start()
    vagas_1_andar.start()
    vagas_2_andar.start()

    lotacao_terreo.start()
    lotacao_1_andar.start()
    lotacao_2_andar.start()

    # Start

    cancela_entrada.start()
    cancela_saida.start()

    transicao_terreo_1.start()
    transicao_1_2.start()

    vagas_terreo.start()
    vagas_1_andar.start()
    vagas_2_andar.start()

    lotacao_terreo.start()
    lotacao_1_andar.start()
    lotacao_2_andar.start()

    # Join

    threading.Thread(target=interface_usuario).start()
    threading.Thread(target=start_socket_server).start()
    app.run(host='0.0.0.0', port=5000)

    cancela_entrada.join()
    cancela_saida.join()

    transicao_terreo_1.join()
    transicao_1_2.join()

    vagas_terreo.join()
    vagas_1_andar.join()
    vagas_2_andar.join()

    lotacao_terreo.join()
    lotacao_1_andar.join()
    lotacao_2_andar.join()

    cancela_entrada.join()
    cancela_saida.join()

    transicao_terreo_1.join()
    transicao_1_2.join()

    vagas_terreo.join()
    vagas_1_andar.join()
    vagas_2_andar.join()

    lotacao_terreo.join()
    lotacao_1_andar.join()
    lotacao_2_andar.join()
