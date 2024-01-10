#Programa para monimentação da mesa de fio
import time
import serial


def move(x):
    ser = serial.Serial('COM4', 115200)
    #deslocamento em mm
    desl = x
    npassos = int(desl*12800/(3.14156535*19.30))
    npst = "PRA = " + str(npassos) +"\r\n"
    npby = bytes(npst, 'utf-8')
    ser.write(b'SHA\r\n')
    ser.write(b'MTA = -2\r\n')
    ser.write(b'CN-11\r\n')
    ser.write(b'SPA = 5000\r\n')
    ser.write(b'ACA = 5000\r\n')
    ser.write(b'DCA = 5000\r\n')
    ser.write(npby)
    ser.write(b'BGA\r\n')
    ser.close()
    

move(100)
time.sleep(8)
move(-100)

