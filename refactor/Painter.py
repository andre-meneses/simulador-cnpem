import socket
import time
from Laser import LaserController
import Mcp
import curses
import numpy as np

class Painter:
    def __init__(self, socket_x, socket_y, calx, caly, mcp, tlaser=0.025):
        self.socket_x = socket_x
        self.socket_y = socket_y
        self.calx = calx
        self.caly = caly
        self.mcp = mcp
        self.tlaser = tlaser
        self.laser = LaserController(mcp)
        self.grid = np.zeros((3,3,2)) 
        # self.grid[0,0,0] = 5.85
        # self.grid[0,0,1] = -5.55
        # self.grid[2,2,0] = -4.64
        # self.grid[2,2,1] = 0.75

    def move(self, axis, position):
        command = f"MWV:{position}\r\n".encode('utf-8')
        (self.socket_x if axis == 'x' else self.socket_y).sendall(command)

    def paint_test(self):
        grid_size = 60
        points = 15
        increment = 4

        for i in range(points):
            posY = (-(grid_size / 2) + i * increment) * self.caly
            self.move('y', posY)
            
            for j in range(points):
                posX = (-(grid_size / 2) + j * increment) * self.calx
                self.move('x', posX)
                self.laser.switch_laser('on')
                time.sleep(self.tlaser)
                self.laser.switch_laser('off')

    def paint_test_rect(self):
        posY = -9
        self.laser.switch_laser('on')
        for i in range(125):
            self.move('y', posY)
            posX = 10
            for j in range(175):
                self.move('x', posX)
                posX -= 0.08
                time.sleep(0.001)
            posY += 0.08
        self.laser.switch_laser('off')

    def paint_manual(self, stdscr):
        posX, posY = 0, 0

        self.move('x', posX)
        self.move('y', posY)

        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)

        self.laser.switch_laser('on')

        while True:
            stdscr.clear()
            stdscr.refresh()

            key = stdscr.getch()
            movement = 0.15

            if key == curses.KEY_UP:
                posY -= movement
            elif key == curses.KEY_DOWN:
                posY += movement
            elif key == curses.KEY_LEFT:
                posX += movement
            elif key == curses.KEY_RIGHT:
                posX -= movement
            elif key == ord('a'):
                self.grid[0,0,0] = posX 
                self.grid[1,0,0] = posX 
                self.grid[2,0,0] = posX 

                self.grid[0,0,1] = posY 
                self.grid[0,1,1] = posY 
                self.grid[0,2,1] = posY 

            elif key == ord('c'):
                self.grid[2,2,0] = posX 
                self.grid[1,2,0] = posX 
                self.grid[0,2,0] = posX 

                self.grid[2,2,1] = posY 
                self.grid[2,1,1] = posY 
                self.grid[2,0,1] = posY 

            elif key == ord('q'):
                break

            self.move('x', posX)
            self.move('y', posY)

        self.laser.switch_laser('off')

        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def interpolate_grid(self):
        for i in range(3):
            self.grid[1,i,1] = (self.grid[0,i,1] + self.grid[2,i,1])/2

        for i in range(3):
            self.grid[i,1,0] = (self.grid[i,2,0] + self.grid[i,0,0])/2

        for i in range(3):
            for j in range(3):
                print(f"{self.grid[i,j,0]} ", end='')
            print("\n")

        for i in range(3):
            for j in range(3):
                print(f"{self.grid[i,j,1]}", end='')
            print("\n")

    def test_calibration(self):
        for i in range(3):
            for j in range(3):
                self.laser.switch_laser('on')
                self.move('x', self.grid[i,j,0])
                self.move('y', self.grid[i,j,1])
                time.sleep(3)

        self.laser.switch_laser('on')

    def kkk(self):
        self.laser.switch_laser('off')

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
    # painter.paint_x(50,2)
    # painter.paint_y(50,2)
    # painter.paint_x(50,2, -1)
    # painter.paint_y(50,2, -1)
    # painter.paint_x(50,2)
    # painter.paint_test_rect()
    # curses.wrapper(painter.paint_manual)
    # painter.interpolate_grid()
    # painter.test_calibration()
    painter.kkk()

