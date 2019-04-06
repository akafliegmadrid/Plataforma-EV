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
from multiprocessing import Process                        # Paquete para ejecucion en paralelo
import time                                                # Funciones relacionadas con el tiempo :/

#### PARAMETROS ####
# Tiempo entre muestras [ms]
sampleTime = 100    # En comms. en serie, siempre hay que dejar un delay entre dos lecturas

# Direccion Bluetooth de los Arduino
btAddr1 = "60:64:05:CF:D3:FC"
btAddr2 = "60:64:05:D0:0F:58"

# UUID de las caracteristicas de lectura
btRead1 = UUID(0xffe1)
btRead2 = UUID(0xffe1)

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
    # Cuando llega una notificacion se escribe en el archivo especificado en "fh"
    def handleNotification(self, cHandle, data):
        write2file(self.dev, self.fh, self.start, data)

# Funcion para crear el archivo log a partir de la fecha en la que se ejecuta el programa
def start_log(num):
    logfileName = time.strftime("%Y_%m_%d_%H_%M.log", time.gmtime())
    logfileName = "sensor{}_".format(num) + logfileName
    logfile = open(logfileName, 'w')
    logfile.write("######### Plataforma EV - Akaflieg Madrid #########\n")
    logfile.write("# Log file creado: " + time.strftime("%c (%Z)", time.localtime()) + " #\n\n")
    startTime = time.time()
    return startTime, logfile

# Funcion de escritura de los datos recibidos
def write2file(dev, fh, start, data):
    data = data.decode('utf-8')
    fh.write("{:<17.6f} {:s}\n".format(time.time()-start, data))
    time.sleep(sampleTime/1000)

# Bucle de ejecucion para cada sensor
def read_sensor(dev, start):
    while (time.time()-start) < 20:     # Provisional :( Deberia controlarse con un boton o algo asi
        dev.waitForNotifications(1.0)   # Se espera como mucho un segundo antes de volver a
                                        # ejecutar el bucle
#### MAIN ####
# Creacion de archivos log
start1, log1 = start_log(btAddr1[-2:])
start2, log2 = start_log(btAddr2[-2:])

# Conexion a los sensores
btDev1 = Peripheral(btAddr1)
btDev2 = Peripheral(btAddr2)

# Seleccion de las caracteristicas de lectura
btCh1 = btDev1.getCharacteristics(uuid=btRead1)[0]
btCh2 = btDev2.getCharacteristics(uuid=btRead2)[0]

# Asignacion del "delegate" (tambien se activan las notificaciones)
btDev1.setDelegate(BtDelegate(btDev1,btCh1.valHandle,log1,start1))
btDev2.setDelegate(BtDelegate(btDev2,btCh2.valHandle,log2,start2))

# Lectura de sensores en paralelo
p1 = Process(target=read_sensor, args=(btDev1,start1))
p2 = Process(target=read_sensor, args=(btDev2,start2))
p1.start()
p2.start()
p1.join()
p2.join()

# Desconexion de los sensores antes de terminar
btDev1.disconnect()
btDev2.disconnect()
