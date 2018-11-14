#!/usr/bin/env python3

import bluetooth
import datetime

# Direccion Bluetooth de los Arduino
port = 1
host = "60:64:05:FC:D3:CF"

socket = bluetooth.BluetoothSocket(RFCOMM)
socket.connect((host,port))

# Se abre el archivo y se escribe todo lo que recibe la RPi
date = datetime.datetime.now()
logfileName = "sensors_{:d}_{:d}_{:d}_{:02d}{:02d}.log".format(date.year,date.month,date.day,date.hour,date.minute)
with open(logfileName, "w") as logfile:
    logfile.write("######### Plataforma EV - Akaflieg Madrid #########\n")
    logfile.write("# Log file creado: " + str(date.now()) + " " + str(date.astimezone().tzinfo) + " #\n\n")
    
    while True:
        data = s.recv(1024)
        logfile.write(str(date.now().time()) + " " + str(data))

# Antes de terminar se cierra la conexion Bluetooth
socket.close()
