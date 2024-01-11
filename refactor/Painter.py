import socket
import math
import time
from mcp2210 import Mcp2210, Mcp2210GpioDesignation, Mcp2210GpioDirection
from Laser import LaserController
import Mcp

class Painter:
    def __init__(self, socket_x, socket_y, calx, caly, mcp, tlaser=0.025):
        self.socket_x = socket_x
        self.socket_y = socket_y
        self.calx = calx
        self.caly = caly
        self.mcp = mcp
        self.tlaser = tlaser
        self.laser = LaserController(mcp)

    def paint_x(self, distance, increment):
        num_points = int(distance / increment)
        start_x = -(distance / 2) * self.calx
        pos_x = start_x

        for _ in range(num_points):        
            pos_x_str = f"MWV:{pos_x}\r\n"
            arr_x = pos_x_str.encode('utf-8')
            self.socket_x.sendall(arr_x)
            time.sleep(self.tlaser)
            self.laser.switch_laser('off')
            pos_x += increment * self.calx
            print(pos_x)

    def paint_y(self, distance, increment):
        num_points = int(distance / increment)
        start_y = -(distance / 2) * self.caly
        pos_y = start_y

        for _ in range(num_points):
            pos_y_str = f"MWV:{pos_y}\r\n"
            arr_y = pos_y_str.encode('utf-8')
            self.socket_y.sendall(arr_y)
            time.sleep(self.tlaser)
            self.laser.switch_laser('off')
            pos_y += increment * self.caly
            print(pos_y)

    def paint_test(self):
        posY =  -(60 / 2) * self.caly
        npontos = 15 
        for i in range(npontos):      
            posYst = "MWV:"+str(posY)+"\r\n"
            arrY = bytes(posYst, 'utf-8')  
            self.socket_y.sendall(arrY)       
            posX =  -(60 / 2) * self.calx
            for j in range (npontos):        
                posXst = "MWV:"+str(posX)+"\r\n"
                arrX = bytes(posXst, 'utf-8')
                self.socket_x.sendall(arrX)
                self.laser.switch_laser('on')
                time.sleep(self.tlaser)
                self.laser.switch_laser('off')
                posX = posX + 4 * calx
                print("Posição x:", posX)
            posY = posY + 4 * caly

        
if __name__ == '__main__':
    host_x = "192.168.0.11"  # Server's IP address
    host_y = "192.168.1.10"  # Server's IP address

    port = 10001  # Port used by the server

    socket_x = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_y = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        socket_x.connect((host_x, port))
        socket_y.connect((host_y, port))
    except socket.error as e:
        print(f"Error connecting to socket: {e}")

    mcp = Mcp.Mcp()
    calx = 20 / (113.41 + 114.21)
    caly = 20 / (153.02 + 154.22)
    
    painter = Painter(socket_x, socket_y, calx, caly, mcp)  # Adjust as needed

    painter.paint_test()

