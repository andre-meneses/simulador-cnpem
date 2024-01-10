# Programa de teste da rotina burn2

import serial
import socket
import time
from mcp2210 import Mcp2210, Mcp2210GpioDesignation, Mcp2210GpioDirection

 
 
# Define a porta e a velocidade de comunicação com o Galil
# O goniômetro foi instalado na saída 8 (H) da eletrônica de controle
# O comando SHH habilita o motor, o comando MTH diz o tipo de motor
# O comando CN1 diz a polaridade do Limit Switch

ser = serial.Serial('COM4', 115200)
ser.write(b'SHH\r\n')
ser.write(b'MTH = -2\r\n')
ser.write(b'CN1\r\n')



# Configuração dos pinos da MCP2010

mcp = Mcp2210(serial_number="0000423978")
mcp.configure_spi_timing(chip_select_to_data_delay=0, last_data_byte_to_cs=0,
                         delay_between_bytes=0)
mcp.set_gpio_designation(0, Mcp2210GpioDesignation.GPIO)

# set pin 0 to output
mcp.set_gpio_direction(0, Mcp2210GpioDirection.OUTPUT)

#desliga o laser caso ele esteja ligado
mcp.set_gpio_output_value(0, False)


# Essa rotina liga o laser

def laser_on():
    mcp.set_gpio_output_value(0, True)

def laser_off():
    mcp.set_gpio_output_value(0, False)


def burn2():
    
    disthor = 100
    offsetX = 1
    offsetY = -3
    increm = 4
    npontos = int(disthor/increm)

    calx = 20/(113.41+114.21)
    caly = 20/(153.02+154.22)

    vinix = -(disthor/2)*calx
    viniy = -(disthor/2)*caly
    

    HOSTY = "192.168.1.10"  # The server's hostname or IP address
    PORT = 10001  # The port used by the server
    sy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sy.connect((HOSTY, PORT))


    HOSTX = "192.168.0.11"  # The server's hostname or IP address
    PORT = 10001  # The port used by the server
    sx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sx.connect((HOSTX, PORT))
    
    

    posY = viniy + offsetY
    laser_on()
    for i in range(npontos):
        posYst = "MWV:"+str(posY)+"\r\n"
        arrY = bytes(posYst, 'utf-8')  
        sy.sendall(arrY)     
        posX = vinix + offsetX       
        posXst = "MWV:"+str(posX)+"\r\n"
        arrX = bytes(posXst, 'utf-8')
        sx.sendall(arrX)
        time.sleep(0.001)
        posX = -vinix + offsetX      
        posXst = "MWV:"+str(posX)+"\r\n"
        arrX = bytes(posXst, 'utf-8')
        sx.sendall(arrX)
        time.sleep(0.001)
        posY = posY + increm * caly
    laser_off()
    ser.close()
    
for j in range(100):
    burn2()
