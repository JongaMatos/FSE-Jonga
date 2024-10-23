### Requisitos 
 
#### Thingsboard 
 
- [x] Cadastro de dispositivos 
- [x] Criação de Tokens dos dispositivos 
- [x] Dashboard 
- [x] Envio de Telemetria e Atributos 
- [ ] Recebimento de Comandos do Dashboard 
 
Thingsboard MQTT API Reference 
 
Cada dispositivo criado no Thingsboard deverá ser configurado com o tipo de transporte (`Tranport Type`) MQTT. A conexão MQTT cujos tópicos para envio de dados são: 
 
Telemetria: v1/devices/me/telemetry 
 
Atributos: v1/devices/me/attributes 
 
O envio e recebimento de comandos deverá ser realizado através de Remote Procedure Calls (RPC), com a documentação descrita na API. Em resumo, o cliente deve se inscrever no tópido v1/devices/me/rpc/request/+ e irá receber cada comando em um subtópico com ID único em v1/devices/me/rpc/response/$request_id. Quanto necessário, a confirmação do comando deve ser retornada pelo mesmo tópico com o ID enviado (`v1/devices/me/rpc/response/$request_id`). O conteúdo de todas as mensagens será sempre no formato Json. 
 
#### Cliente ESP32 
 
- [ ] Definição dos modos Energia e Bateria (Deve ser escolhido através do menuconfig); 
- [x] Conexão WIFI (Credenciais devem ser definidas através do menuconfig); 
- [ ] Cada cliente ESP32 ao ser inicializado deverá: 
        - [x] Inicializar o serviço MQTT e conectar ao broker com o token de acesso do dispositivo; 
        - [x] Se inscrever no tópico v1/devices/me/rpc/request/+ para recebimento de comandos remotos; 
        - [x] Enviar telemetria e atributos pelos respectivos tópicos da API. 
- [ ] Armazenar os estados dos atributos (estado das saídas) em caso de reinicio do dispositivo por falta de energia. Deve armazenar em NVS; 
- [ ] Realizar a telemetria dos sensores selecionados e atualização do dashboard de maneira periódica (no mínimo a cada 1 segundo); 
- [ ] Monitorar o botão utilizando interrupções e enviar por mensagem push a cada mudança do estado do botão; (???) 
- [ ] Acionar Saídas como o LED, dentre outras, à partir dos comandos RPC enviandos pelo Dashboard de maneira dimerizável, sua intensidade controlada à partir da técnica PWM 
 
Observação: A versão da ESP32 operando por bateria deverá ter as mesmas características de comunicação descritas acima, porém, será utilizada exclusivamente para acionamento de sensores (entradas) operando em modo low power e enviando o estado de seu sensor via push sempre que houver uma mudança de estado. Neste caso, não haverá um sensor de temperatura / umidade acoplado. 
 
### Sensores Obrigatórios 
 
- [x] LED (saídas); 
- [x] Botão (input da ESP32); 
- [x] Tela OLED 0.96; 
- [x] Sensor de temperatura (qualquer sensor digital ou analógico); 
- [x] Pelo menos um sensor com entrada analógica. 
 
### Sensores Utilizados 
 
- 1 Tela OLED - Saída: Sem PWM 
- 1 LED RGB - Saída: Com PWM 
- 1 Buzzer - Saída: Com PWM 
- 3 LED da placa - Saída: Com PWM 
- 3 Botão da placa - Entrada Digital 
- 1 Sensor de Temperatura - Entrada Digital 
- 1 Sensor de Fotovoltagem - Entrada Analógica 
- 1 Sensor de Som - Entrada Analógica e Digital 
 
### Sensores Mínimos 
 
- 3 Saídas / Incluindo acionamento modo PWM 
- 3 Entradas Digitais 
- 1 Entrada Analógica