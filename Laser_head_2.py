#Programa para calibração do cabeçote
import socket
import time
from mcp2210 import Mcp2210, Mcp2210GpioDesignation, Mcp2210GpioDirection


from pynput import keyboard
from pynput.keyboard import Key


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




posYini = -9.0
posXini = 10.0
delta = 0.08



HOSTY = "192.168.1.10"  # The server's hostname or IP address
PORT = 10001  # The port used by the server
sy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sy.connect((HOSTY, PORT))


HOSTX = "192.168.0.11"  # The server's hostname or IP address
PORT = 10001  # The port used by the server
sx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sx.connect((HOSTX, PORT))

laser_on()

posY = posYini
for i in range (125):
    posYst = "MWV:"+str(posY)+"\r\n"
    arrY = bytes(posYst, 'utf-8')
    sy.sendall(arrY)
    posX = posXini
    for j in range (175):
        posXst = "MWV:"+str(posX)+"\r\n"
        arrX = bytes(posXst, 'utf-8')  
        sx.sendall(arrX)
        posX = posX - delta
        time.sleep(0.001)
    posY = posY + delta
        
laser_off()




    
