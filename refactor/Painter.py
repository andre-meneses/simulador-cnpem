#Programa de teste do cabeçote laser
import socket
import time
from mcp2210 import Mcp2210, Mcp2210GpioDesignation, Mcp2210GpioDirection
import Laser
import Mcp

class Painter(socket_x, socket_y, calx, caly, tlaser = 0.025)

    def __init__():
        self.socket_x = socket_x
        self.socket_y = socket_y
        self.distancia_h = distancia_h
        self.incremento = incremento
        self.calx = calx
        self.caly = caly

    def paint_x(distancia, incremento):
        n_pontos = int(distancia/incremento)



mcp = Mcp.Mcp()
   
#assumindo que na projeção no papel temos que 10v = 111mm
disthor = 60
increm = 4

calx = 20/(113.41+114.21)
# caly = 20/(153.02+154.22)

vinix = -(disthor/2)*calx
# viniy = -(disthor/2)*caly
npontos = int(disthor/increm)



# HOSTY = "192.168.1.10"  # The server's hostname or IP address
PORT = 10001  # The port used by the server

# sy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sy.connect((HOSTY, PORT))


HOSTX = "192.168.0.11"  # The server's hostname or IP address
PORT = 10001  # The port used by the server
sx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sx.connect((HOSTX, PORT))

posX = vinix
for j in range (npontos):        
    posXst = "MWV:"+str(posX)+"\r\n"
    arrX = bytes(posXst, 'utf-8')
    sx.sendall(arrX)
    Laser.switch_laser(mcp,'on')
    time.sleep(tlaser)
    Laser.switch_laser(mcp,'off')
    posX = posX + increm * calx
    print(posX)

