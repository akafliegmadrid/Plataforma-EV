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
import smbus                                               # Conexiones mediante I2C y SPI

#### PARAMETROS ####
# Tiempo entre muestras [ms]
sampleTime = 200

# Direccion I2C de la IMU
IMUaddr = 0x53

# Direccion Bluetooth de los Arduino
btAddr1 = "60:64:05:CF:D3:FC"
btAddr2 = "60:64:05:D0:0F:58"

# UUID de las caracteristicas de lectura
btRead1 = UUID(0xffe1)
btRead2 = UUID(0xffe1)

# Definicion de pines
startStopBtn = 17   # [GPIO17] Boton que inicia/detiene la lectura BT (Pull-up)
thermalBtn   = 27   # [GPIO27] Boton que inicia/detine el indicador de termicas
readingLED   = 22   # [GPIO22] LED que indica que se están guardando datos
thermalLED   = 23   # [GPIO23] LED que indica que el indicador de termicas esta activado

# Tiempo que hay que mantener pulsado el boton de inicio/parada [ms]
startStopThres = 1000

# Texto que se escribe en los logs cuando se pulsa el boton de termica
thermalToggleString = "--> Thermal Toggle <--"

#### FUNCIONES ####
# Funcion handle de las notificaciones
class BtDelegate(DefaultDelegate):
    # Al principio se activan las notificaciones y se guardan algunas variables necesarias despues
    def __init__(self, dev, chHandle):
        self.fh = fh
        DefaultDelegate.__init__(self)
        dev.writeCharacteristic(chHandle+1, b'\x01\x00')
    # Cuando llega una notificacion se escribe en el archivo especificado en "fh"
    def handleNotification(self, cHandle, data):
        write2file(self.fh, data)

# Funcion para crear el archivo log a partir de la fecha en la que se ejecuta el programa
def start_log(num):
    logfileName = time.strftime("%Y_%m_%d_%H_%M_%S.log", time.gmtime())
    logfileName = "sensor{}_".format(num) + logfileName
    logfile = open(logfileName, 'w')
    logfile.write("######### Plataforma EV - Akaflieg Madrid #########\n")
    logfile.write("# Log file creado: " + time.strftime("%c (%Z)", time.localtime()) + " #\n\n")
    startTime = time.time()
    return startTime, logfile

# Funcion de escritura de los datos recibidos
def write2file(fh, data):
    data = data.decode('utf-8')
    fh.write(data)

# Funcion de lectura y escritura de los datos de la IMU en log
def saveIMUstate(dev, devAddr, log, startTime):
    buf = dev.read_i2c_block_data(devAddr, 0x32, 8)
    ax, ay, az = struct.unpack('<ff', buf)
    log.write("{},{},{},{}".format(time.time()-startTime, ax, ay, az))

#### MAIN ####
# Interfaces GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(startStopBtn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(thermalBtn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(readingLED, GPIO.OUT)
GPIO.setup(thermalLED, GPIO.OUT)
GPIO.output(readingLED, GPIO.LOW)
GPIO.output(thermalLED, GPIO.LOW)

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

        # Se enciende el LED
        GPIO.output(readingLED, GPIO.HIGH)

        # Delay de 3 segundos tras el inicio
        time.sleep(3)

        # Creacion de archivos log
        startBT1, logBT1 = start_log(btAddr1[-2:])
        startBT2, logBT2 = start_log(btAddr2[-2:])
        startIMU, logIMU = start_log("IMU")

        # Conexion a los sensores
        btDev1 = Peripheral(btAddr1)
        btDev2 = Peripheral(btAddr2)

        # Seleccion de las caracteristicas de lectura
        btCh1 = btDev1.getCharacteristics(uuid=btRead1)[0]
        btCh2 = btDev2.getCharacteristics(uuid=btRead2)[0]

        # Asignacion del "delegate" (tambien se activan las notificaciones)
        btDev1.setDelegate(BtDelegate(btDev1,btCh1.valHandle,logBT1))
        btDev2.setDelegate(BtDelegate(btDev2,btCh2.valHandle,logBT2))

        # Creacion de la conexion con la IMU
        IMU = smbus.SMBus(0)

        # Lectura de sensores en serie
        StartStopPressed = False
        thermalPressed   = False
        thermalLEDState  = False
        while True:
            # Se sale del modo de medida si se pulsa el boton
            if not GPIO.input(startStopBtn) and not pressed:
                startTime = time.time()
                StartStopPressed = True
            elif GPIO.input(startStopBtn):
                startTime = time.time()
                StartStopPressed = False
            # Se cambia el modo termica si se pulsa el boton
            if not GPIO.input(thermalBtn) and not thermalPressed:
                logBT1.write(thermalToggleString)
                logBT2.write(thermalToggleString)
                thermalPressed = True
                thermalLEDState = not thermalLEDState
                GPIO.output(thermalLED, thermalLEDState)
            elif GPIO.input(thermalBtn):
                thermalPressed = False
            while btDev1.waitForNotifications(sampleTime/1000): pass
            while btDev2.waitForNotifications(sampleTime/1000): pass
            # Se guarda el estado de la IMU antes de comprobar si se sale del bucle
            saveIMUstate(IMU, IMUaddr, logIMU)
            if not GPIO.input(startStopBtn) and time.time()-startTime >= startStopThres/1000: break

        # Archivos log terminados
        logBT1.close()
        logBT2.close()

        # Desconexion de los sensores antes de terminar
        btDev1.disconnect()
        btDev2.disconnect()

        # Se apaga el LED
        GPIO.output(readingLED, GPIO.LOW)

        # Delay de 3 segundos hasta que se pueda iniciar otra vez
        time.sleep(3)

except KeyboardInterrupt:
    GPIO.cleanup()
