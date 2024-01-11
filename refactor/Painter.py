import socket
import time
from Laser import LaserController
import Mcp

class Painter:
    """
    This class is designed to control a laser painting system that operates in a two-dimensional space.

    Attributes:
        socket_x (socket.socket): A socket object for communication with the X-axis controller.
        socket_y (socket.socket): A socket object for communication with the Y-axis controller.
        calx (float): Calibration factor for movements along the X-axis.
        caly (float): Calibration factor for movements along the Y-axis.
        mcp (Mcp): An object to interface with the MCP2210 chip for controlling the laser.
        tlaser (float): Time delay for the laser between movements, in seconds.
        laser (LaserController): An object to control the on/off state of the laser.
    """

    def __init__(self, socket_x, socket_y, calx, caly, mcp, tlaser=0.025):
        """
        Initializes a new Painter instance.

        Args:
            socket_x (socket.socket): Socket for X-axis control.
            socket_y (socket.socket): Socket for Y-axis control.
            calx (float): Calibration factor for X-axis.
            caly (float): Calibration factor for Y-axis.
            mcp (Mcp): MCP2210 interface object.
            tlaser (float, optional): Laser time delay. Defaults to 0.025 seconds.
        """
        self.socket_x = socket_x
        self.socket_y = socket_y
        self.calx = calx
        self.caly = caly
        self.mcp = mcp
        self.tlaser = tlaser
        self.laser = LaserController(mcp)

    def paint_x(self, distance, increment, axis=1):
        """
        Moves the laser along the X-axis and paints over a specified distance with specified increments.

        Args:
            distance (float): The total distance to move and paint along the X-axis.
            increment (float): The distance between each point in the painting process along the X-axis.
        """
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
            if axis==-1:
                pos_x -= increment * self.calx
            else:
                pos_x += increment * self.calx
            print(pos_x)

    def paint_y(self, distance, increment, axis=1):
        """
        Moves the laser along the Y-axis and paints over a specified distance with specified increments.

        Args:
            distance (float): The total distance to move and paint along the Y-axis.
            increment (float): The distance between each point in the painting process along the Y-axis.
        """
        num_points = int(distance / increment)
        start_y = -(distance / 2) * self.caly
        pos_y = start_y

        for _ in range(num_points):
            pos_y_str = f"MWV:{pos_y}\r\n"
            arr_y = pos_y_str.encode('utf-8')
            self.socket_y.sendall(arr_y)
            self.laser.switch_laser('on')
            time.sleep(self.tlaser)
            self.laser.switch_laser('off')

            if axis==-1:
                pos_y -= increment * self.caly
            else:
                pos_y += increment * self.caly

            print(pos_y)

    def paint_test(self):
        """
        Conducts a test painting routine by moving the laser in a grid pattern and activating the laser at each grid point.
        """
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
                posX = posX + 4 * self.calx
                print("Posição x:", posX)
            posY = posY + 4 * self.caly        

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

    # painter.paint_test()
    painter.paint_x(50,2)
    painter.paint_y(50,2)
    painter.paint_x(50,2, -1)
    painter.paint_y(50,2, -1)
    painter.paint_x(50,2)

