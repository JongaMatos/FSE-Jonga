import RPi.GPIO as GPIO
from time import sleep
from pid import PID

import comandos

class GPIOController:

    def __init__(self, numero_elevador=1) -> None:

        self.pid=PID()
        
        GPIO.setwarnings(False)
        
        self.id_motor=numero_elevador-1
        self.status = None

        self.terreo = 40
        self.andar1 = 6520
        self.andar2 = 10960
        self.andar3 = 17400

        self.andar_atual = None
        self.nome_andar = None
        self.vel = None
        
        if (numero_elevador == 1):
            
            self.DIR1_PIN = 20
            self.DIR2_PIN = 21
            self.PWM_PIN = 12
            
            self.SENSOR_TERREO_PIN = 18
            self.SENSOR_1_ANDAR_PIN = 23
            self.SENSOR_2_ANDAR_PIN = 24
            self.SENSOR_3_ANDAR_PIN = 25

        elif (numero_elevador == 2):
            
            self.DIR1_PIN = 19
            self.DIR2_PIN = 26
            self.PWM_PIN = 13
            
            self.SENSOR_TERREO_PIN = 17
            self.SENSOR_1_ANDAR_PIN = 27
            self.SENSOR_2_ANDAR_PIN = 22
            self.SENSOR_3_ANDAR_PIN = 6

        else:
            raise Exception("numero_elevador must be 1 or 2")

        GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(self.DIR1_PIN, GPIO.OUT)
        GPIO.setup(self.DIR2_PIN, GPIO.OUT)
        GPIO.setup(self.PWM_PIN, GPIO.OUT)
        
        GPIO.setup(self.SENSOR_TERREO_PIN, GPIO.IN)
        GPIO.setup(self.SENSOR_1_ANDAR_PIN, GPIO.IN)
        GPIO.setup(self.SENSOR_2_ANDAR_PIN, GPIO.IN)
        GPIO.setup(self.SENSOR_3_ANDAR_PIN, GPIO.IN)

        self.motor_pwm = GPIO.PWM(self.PWM_PIN, 1000)

    # Metodos
    def __inicia_pwm(self) -> None:
        self.motor_pwm.start(100)

    def __para_pwm(self) -> None:
        self.motor_pwm.stop()
        self.aciona_motor('livre')

    def encerra(self)->None:
        self.__para_pwm()

    def __definir_potencia_pwm(self, potencia_percentual: float) -> None:
        """
            Recebe valor entre 0 e 100, representando o percentual da potencia (de 0% a 100%).
        """
        self.motor_pwm.ChangeDutyCycle(potencia_percentual)

    def __atualiza_estados(self, DIR1: bool, DIR2: bool, potencia: float, status: str) -> None:
        GPIO.output(self.DIR1_PIN, DIR1)
        GPIO.output(self.DIR2_PIN, DIR2)
        self.__definir_potencia_pwm(potencia)
        self.vel=potencia
        self.status = status

    def aciona_motor(self, sentido: str, potencia_percentual: float = 100) -> None:
        if sentido == 'sobe':
            self.__atualiza_estados(1, 0, potencia_percentual, 'Subindo')
        elif sentido == 'desce':
            self.__atualiza_estados(0, 1, potencia_percentual, 'Descendo')
        elif sentido == 'freio':
            self.__atualiza_estados(1, 1, potencia_percentual, 'Parado')
        elif sentido == 'livre':
            self.__atualiza_estados(0, 0, 0, 'Parado')

    def verificar_sensores(self):
        return {
            "Terreo": GPIO.input(self.SENSOR_TERREO_PIN),
            "1o Andar": GPIO.input(self.SENSOR_1_ANDAR_PIN),
            "2o Andar": GPIO.input(self.SENSOR_2_ANDAR_PIN),
            "3o Andar": GPIO.input(self.SENSOR_3_ANDAR_PIN),
        }
    
    def calibra(self) -> None:
        print(f"Inicia calibragem de elevador {self.id_motor+1}")
        self.__inicia_pwm()
        self.aciona_motor('sobe', 10)


        while True:
            
            sensores = self.verificar_sensores()

            if sensores["Terreo"] == 1:
                print(f"Terreo identificado")
                self.terreo = comandos.apurar_encoder(self.id_motor)
                print(f"Terreo identificado")
                
                self.nome_andar = 'Terreo'

            if sensores["1o Andar"] == 1:
                print(f"1o Andar identificado")
                self.andar1 = comandos.apurar_encoder(self.id_motor)
                print(f"1o Andar identificado")
                
                self.nome_andar = '1o Andar'

            if sensores["2o Andar"] == 1:
                print(f"2o Andar identificado")
                self.andar2 = comandos.apurar_encoder(self.id_motor)
                print(f"2o Andar identificado")
                self.nome_andar = '2o Andar'

            if sensores["3o Andar"] == 1:
                print(f"3o Andar identificado")
                self.andar3 = comandos.apurar_encoder(self.id_motor)
                print(f"3o Andar identificado")
                
                self.nome_andar = '3o Andar'

            if self.terreo and self.andar1 and self.andar2 and self.andar3:
                self.__para_pwm()
                print("teste")
                break

            elif self.andar3 and (
                    not self.andar3 or
                    not self.andar2 or
                    not self.andar1 or
                    not self.terreo):
                self.aciona_motor('desce', 22)

            comandos.apurar_pwm(self.id_motor, self.vel)
        print(f"Concluida calibragem de elevador {self.id_motor+1}")
            
    def desce_tudo(self):


        self.__inicia_pwm()

        while True:
            self.aciona_motor('desce')
            self.andar_atual = comandos.apurar_encoder(self.id_motor)

            if self.andar_atual is None:
                return

            self.vel = 100
            comandos.apurar_pwm(self.id_motor, self.vel)

            if self.andar_atual < 50:
                self.aciona_motor('freio')
                return
            
    def update(self, regs):
        self.regs=regs
        
    def ir_para(self, andar):
        
        alvo=40
        self.pid = PID()
        self.__inicia_pwm()
        self.andar_atual = comandos.apurar_encoder(self.id_motor)

        if andar == 0:
            self.pid.atualiza_referencia(self.terreo)
            # alvo=self.terreo
            
            if self.andar_atual - self.terreo > 40:
                while self.andar_atual > self.terreo + 40:
                    print(self.andar_atual-self.terreo)
                    self.aciona_motor('desce', self.pid.controle(comandos.apurar_encoder(self.id_motor)))
                    self.vel = self.pid.controle(self.andar_atual)
                    self.andar_atual=comandos.apurar_encoder(self.id_motor)
                self.__para_pwm()

        elif andar == 1:

            self.pid.atualiza_referencia(self.andar1)
            alvo=self.andar1
            
            if self.andar_atual - self.andar1 > 40:
                while self.andar_atual > self.andar1 + 40:
                    self.andar_atual = comandos.apurar_encoder(self.id_motor)
                    
                    self.aciona_motor('desce', abs(self.pid.controle(comandos.apurar_encoder(self.id_motor))))
                    self.vel = self.pid.controle(self.andar_atual)
                    self.andar_atual=comandos.apurar_pwm(self.id_motor, self.vel)
                self.__para_pwm()
            elif self.andar_atual - self.andar1 < -40:
                while self.andar_atual < self.andar1 - 40:
                    self.aciona_motor('sobe', abs(self.pid.controle(comandos.apurar_encoder(self.id_motor))))
                    self.vel = self.pid.controle(self.andar_atual)
                    self.andar_atual=comandos.apurar_pwm(self.id_motor, self.vel)
                    self.__para_pwm()

            self.pid.controle(self.andar_atual)

        elif andar == 2:
            alvo=self.andar2
            self.pid.atualiza_referencia(self.andar2)
            self.pid.controle(self.andar_atual)

        elif andar == 3:
            alvo=self.andar2
            self.pid.atualiza_referencia(self.andar3)
            self.pid.controle(self.andar_atual)

        else:
            return None
        self.pid.atualiza_referencia(andar)

        while True:
            self.aciona_motor('sobe', self.pid.controle(self.andar_atual))
            self.andar_atual = comandos.apurar_encoder(self.id_motor)
            if self.andar_atual >= alvo:
                self.__para_pwm()
                break
            
