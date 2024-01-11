import socket
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
            self.laser.switch_laser('on')
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
            Laser.switch_laser(self.mcp, 'on')
            time.sleep(self.tlaser)
            Laser.switch_laser(self.mcp, 'off')
            pos_y += increment * self.caly
            print(pos_y)

if __name__ == '__main__':
    host_x = "192.168.0.11"  # Server's IP address
    port = 10001  # Port used by the server
    socket_x = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        socket_x.connect((host_x, port))
    except socket.error as e:
        print(f"Error connecting to socket: {e}")
        # Handle error appropriately

    mcp = Mcp.Mcp()
    calx = 20 / (113.41 + 114.21)
    caly = 20 / (153.02 + 154.22)
    
    painter = Painter(socket_x, None, calx, caly, mcp)  # Adjust as needed
    painter.paint_x(60, 4)  # Example usage

