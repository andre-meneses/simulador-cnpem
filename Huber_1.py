#Programa de movimentação do goniometro huber
import serial
ser = serial.Serial('COM4', 115200)
ser.write(b'SHH\r\n')
ser.write(b'MTH = -2\r\n')
ser.write(b'CN1\r\n')
ser.write(b'SPH = 50000\r\n')
ser.write(b'PRH = 200000\r\n')
ser.write(b'BGH\r\n')
ser.close()
