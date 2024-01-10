#Programa de teste do cabeçote laser
import socket
import time
from mcp2210 import Mcp2210, Mcp2210GpioDesignation, Mcp2210GpioDirection

# Configuração dos pinos da MCP2010

mcp = Mcp2210(serial_number="0000423978")
mcp.configure_spi_timing(chip_select_to_data_delay=0, last_data_byte_to_cs=0,
                         delay_between_bytes=0)
mcp.set_gpio_designation(0, Mcp2210GpioDesignation.GPIO)

# set pin 0 to output
mcp.set_gpio_direction(0, Mcp2210GpioDirection.OUTPUT)

#desliga o laser caso ele esteja ligado
mcp.set_gpio_output_value(0, False)


# Essas rotinas ligam e desligam o laser
def laser_on():
    mcp.set_gpio_output_value(0, True)

def laser_off():
    mcp.set_gpio_output_value(0, False)
    

#assumindo que na projeção no papel temos que 10v = 111mm
disthor = 60
increm = 4

calx = 20/(113.41+114.21)
caly = 20/(153.02+154.22)

vinix = -(disthor/2)*calx
viniy = -(disthor/2)*caly
npontos = int(disthor/increm)

tlaser = 0.025


HOSTY = "192.168.1.10"  # The server's hostname or IP address
PORT = 10001  # The port used by the server

sy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sy.connect((HOSTY, PORT))


HOSTX = "192.168.0.11"  # The server's hostname or IP address
PORT = 10001  # The port used by the server
sx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sx.connect((HOSTX, PORT))


posY = viniy
for i in range(npontos):      
    posYst = "MWV:"+str(posY)+"\r\n"
    arrY = bytes(posYst, 'utf-8')  
    sy.sendall(arrY)       
    posX = vinix
    for j in range (npontos):        
        posXst = "MWV:"+str(posX)+"\r\n"
        arrX = bytes(posXst, 'utf-8')
        sx.sendall(arrX)
        laser_on()
        time.sleep(tlaser)
        laser_off()
        posX = posX + increm * calx
#                   print("Posição x:", posX)
    posY = posY + increm * caly
#    print("*********************************Posição Y:", posY)


