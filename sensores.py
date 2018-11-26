#!/usr/bin/env python3

from bluepy.btle import UUID, Peripheral, DefaultDelegate
import time
from multiprocessing import Process
import struct

#### INPUTS ####
# Tiempo entre muestras [ms]
sampleTime = 100

# Direccion Bluetooth de los Arduino
btAddr1 = "60:64:05:CF:D3:FC"
btAddr2 = "60:64:05:D0:0F:58"

# UUID de las caracteristicas de lectura
btRead1 = UUID(0xffe1)
btRead2 = UUID(0xffe1)

#### MAIN ####
# Funcion handle de las notificaciones
class BtDelegate(DefaultDelegate):
    def __init__(self, dev, chHandle):
        DefaultDelegate.__init__(self)
        dev.writeCharacteristic(chHandle+1, b'\x01\x00')
    def handleNotification(self, cHandle, data):
        return data

# Funcion para crear el archivo log
def start_log(num):
    logfileName = time.strftime("%Y_%m_%d_%H_%M.log", time.gmtime())
    logfileName = "sensor{}_".format(num) + logfileName
    logfile = open(logfileName, 'w')
    logfile.write("######### Plataforma EV - Akaflieg Madrid #########\n")
    logfile.write("# Log file creado: " + time.strftime("%c (%Z)", time.localtime()) + " #\n\n")
    startTime = time.time()
    return startTime, logfile

# Funcion de lectura para los sensores
def read(dev, fh, start):
    while time.time()-start < 20
        data = dev.waitForNotifications(1.0)
        data = data.decode('utf-8')
        fh.write("{:17.6f} {:s}\n".format(time.time()-start, data))
        time.sleep(sampleTime)

# Conexion a los sensores
btDev1 = Peripheral(btAddr1)
btDev2 = Peripheral(btAddr2)

# Seleccion de las caracteristicas de lectura
btCh1 = btDev1.getCharacteristics(uuid=btRead1)[0]
btCh2 = btDev2.getCharacteristics(uuid=btRead2)[0]
btDev1.setDelegate(BtDelegate(btDev1,btCh1.valHandle))
btDev2.setDelegate(BtDelegate(btDev2,btCh2.valHandle))

# Creacion de archivos log
start1, log1 = start_log(1)
start2, log2 = start_log(2)

# Lectura de sensores
p1 = Process(target=read, args=(btDev1,log1,start1))
p2 = Process(target=read, args=(btDev2,log2,start2))
p1.start()
p2.start()
p1.join()
p2.join()

# Desconexion de los sensores antes de terminar
btDev1.disconnect()
btDev2.disconnect()
