#!/usr/bin/env python3

"""
La comunicacion con dispositivos BLE se realiza a través de servicios, caracteristicas y
descriptores:

+ Servicio 1
  - Caracteristica 1
    ~ Propiedades
    ~ Valores
    ~ Descriptores
  - Caracteristica 2
    ~ Propiedades
    ~ Valores
    ~ Descriptores
+ Servicio 2
  - Caracteristica 1
    ~ Propiedades
    ~ Valores
    ~ Descriptores
       .
       .
       .

Para el HM-10 existen tres servicios, siendo el ultimo el que permite la comunicacion. Este
servicio tiene una caracteristica a la que se puede acceder mediante su UUID y, a su vez,
esta caracteristica tiene un campo para el valor y, al menos, un descriptor. Este descriptor
determina si la funcion de notificacion esta activada (0x01:0x00) o desactivada (creo que es
0x00:0x00). Asi, para comenzar la comunicacion hay que conectar la RPi al disp. HM-10 y escribir
"0x01:0x00" en el primer descriptor de la ultima caracteristica. Despues, se crea un "delegate"
encargado de recibir los nuevos datos tras la notificacion y guardarlos en un archivo.

Refs:
+ https://www.bluetooth.com/specifications/gatt/generic-attributes-overview
+ https://es.wikipedia.org/wiki/Identificador_%C3%BAnico_universal
"""

from bluepy.btle import UUID, Peripheral, DefaultDelegate  # Solo se importan esos tres objetos
import RPi.GPIO as GPIO                                    # Pines GPIO
import time                                                # Funciones relacionadas con el tiempo

#### PARAMETROS ####
# Tiempo entre muestras [ms]
sampleTime = 200

# Direccion Bluetooth de los Arduino
btAddrs = [ "60:64:05:CF:D3:FC", \
            "60:64:05:D0:0F:58"  ]

# UUID de las caracteristicas de lectura
btReads = [ UUID(0xffe1), \
            UUID(0xffe1)  ]

# Definicion de pines
startStopBtn = 2    # Boton que inicia/detiene la lectura BT (Pull-up)
readingLED   = 3    # LED que indica que se están guardando datos

# Tiempo que hay que mantener pulsado el boton de inicio/parada [ms]
startStopThres = 1000

#### FUNCIONES ####

# Funcion handle de las notificaciones
class BtDelegate(DefaultDelegate):

    # Al principio se activan las notificaciones y se guardan algunas variables necesarias despues
    def __init__(self, dev, chHandle, fh, start):
        self.dev = dev
        self.fh = fh
        self.start = start
        DefaultDelegate.__init__(self)
        dev.writeCharacteristic(chHandle+1, b'\x01\x00')

    # Cuando llega una notificacion se escribe en el archivo especificado en "fh" y el LED se
    # apaga mientras dura la transmision
    def handleNotification(self, cHandle, data):
        GPIO.output(readingLED, GPIO.LOW)
        write2file(self.dev, self.fh, self.start, data)
        GPIO.output(readingLED, GPIO.HIGH)

# Funcion para crear el archivo log a partir de la fecha en la que se ejecuta el programa
def start_log(num):
    logfileName = time.strftime("%Y_%m_%d_%H_%M_%S.log", time.gmtime())
    logfileName = "EV{}_".format(num) + logfileName
    logfile = open(logfileName, 'w')
    logfile.write("######### Plataforma EV - Akaflieg Madrid #########\n")
    logfile.write("# Log file creado: " + time.strftime("%c (%Z)", time.localtime()) + " #\n")
    startTime = time.time()
    return startTime, logfile

# Funcion de escritura de los datos recibidos
def write2file(dev, fh, start, data):
    data = data.decode('utf-8')
    fh.write(data)

def initRead(addrs, chars):
    logs = []
    devs = []

    for (btAddr, btRead) in zip(addrs, chars):

        # Creacion de archivos log
        start, logThis = start_log(btAddr[-2:])
        logs.append(logThis)

        # Conexion a los sensores
        btDev = Peripheral(btAddr)
        devs.append(btDev)

        # Seleccion de las caracteristicas de lectura
        btCh = btDev.getCharacteristics(uuid=btRead)[0]

        # Asignacion del "delegate" (tambien se activan las notificaciones)
        btDev.setDelegate(BtDelegate(btDev,btCh.valHandle,logThis,start))

    return logs, devs

def endRead(logs, devs):
    for (log, dev) in zip(logs, devs):
        log.close()
        dev.disconnect()

#### MAIN ####

# Interfaces GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(startStopBtn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(readingLED, GPIO.OUT)
GPIO.output(readingLED, GPIO.LOW)

try:
    while True:
        # Se empiezan las medidas si el boton esta pulsado 'startStopThres' milisegundos
        pressed = False
        while True:
            if not GPIO.input(startStopBtn) and not pressed:
                startTime = time.time()
                pressed   = True
            elif GPIO.input(startStopBtn):
                startTime = time.time()
                pressed   = False
            if (time.time()-startTime) >= startStopThres/1000: break

        # Al comenzar, el LED se enciende durante 3s y luego se apaga
        GPIO.output(readingLED, GPIO.HIGH)
        time.sleep(3)

        # Se inician los archivos log y la conexion a los Bluetooth
        logs, devs = initRead(btAddrs, btReads)

        # Lectura de sensores en serie
        pressed = False
        while True:

            # Comprobar si el boton se ha pulsado
            if not GPIO.input(startStopBtn) and not pressed:
                startTime = time.time()
                pressed   = True
            elif GPIO.input(startStopBtn):
                startTime = time.time()
                pressed   = False

            # Lectura de los Bluetooth
            for dev in devs:
                while dev.waitForNotifications(sampleTime/1000): pass

            # Si el boton esta pulsado durante el tiempo suficiente, se termina el bucle
            if not GPIO.input(startStopBtn) and time.time()-startTime >= startStopThres/1000: break

        # Archivos log terminados
        endRead(logs, devs)

        # Se apaga el LED
        GPIO.output(readingLED, GPIO.LOW)

        # Delay de 3 segundos hasta que se pueda iniciar otra vez
        time.sleep(3)

except KeyboardInterrupt:
    GPIO.cleanup()
