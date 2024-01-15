import socket
import time
from Laser import LaserController
import Mcp
import curses
import numpy as np

class LaserPainter:
    """
    Class to control a laser painter device, capable of moving along X and Y axes,
    and controlling a laser for drawing or painting.

    Attributes:
        x_socket (socket.socket): Socket for controlling the X-axis.
        y_socket (socket.socket): Socket for controlling the Y-axis.
        x_calibration_factor (float): Calibration factor for X-axis movements.
        y_calibration_factor (float): Calibration factor for Y-axis movements.
        mcp_controller (Mcp): Controller for MCP hardware.
        laser_pulse_duration (float): Duration for which the laser stays on during painting.
        laser_controller (LaserController): Controller for the laser.
        calibration_grid (numpy.ndarray): Grid for calibration data.
    """

    def __init__(self, x_socket, y_socket, x_cal_factor, y_cal_factor, mcp_controller, laser_pulse_duration=0.025):
        """
        Initializes the LaserPainter with sockets, calibration factors, MCP controller, and laser settings.

        Args:
            x_socket (socket.socket): Socket for controlling the X-axis.
            y_socket (socket.socket): Socket for controlling the Y-axis.
            x_cal_factor (float): Calibration factor for X-axis movements.
            y_cal_factor (float): Calibration factor for Y-axis movements.
            mcp_controller (Mcp): Controller for MCP hardware.
            laser_pulse_duration (float): Duration for the laser pulse. Defaults to 0.025 seconds.
        """
        self.x_socket = x_socket
        self.y_socket = y_socket
        self.x_calibration_factor = x_cal_factor
        self.y_calibration_factor = y_cal_factor
        self.mcp_controller = mcp_controller
        self.laser_pulse_duration = laser_pulse_duration
        self.laser_controller = LaserController(mcp_controller)
        self.calibration_grid = np.zeros((3, 3, 2))

        self.x_socket.sendall(b'UPMODE:NORMAL\r\n')
        self.y_socket.sendall(b'UPMODE:NORMAL\r\n')

    def move(self, axis, position):
        """
        Moves the laser painter along the specified axis to the given position.

        Args:
            axis (str): The axis along which to move ('x' or 'y').
            position (float): The position to move to.
        """
        command = f"MWV:{position}\r\n".encode('utf-8')
        (self.x_socket if axis == 'x' else self.y_socket).sendall(command)

    def paint_pattern_1(self):
        """
        Executes a predefined painting pattern 1.
        """
        grid_size = 60
        points = 15
        increment = 4

        for i in range(points):
            posY = (-(grid_size / 2) + i * increment) * self.y_calibration_factor
            self.move('y', posY)
            
            for j in range(points):
                posX = (-(grid_size / 2) + j * increment) * self.x_calibration_factor
                self.move('x', posX)
                self.laser_controller.switch_laser('on')
                time.sleep(self.laser_pulse_duration)
                self.laser_controller.switch_laser('off')

    def paint_pattern_2(self):
        """
        Executes a predefined painting pattern 2.
        """
        posY = -9
        self.laser_controller.switch_laser('on')
        for i in range(125):
            self.move('y', posY)
            posX = 10
            for j in range(175):
                self.move('x', posX)
                posX -= 0.08
                time.sleep(0.001)
            posY += 0.08
        self.laser_controller.switch_laser('off')

    def paint_manually(self, stdscr):
        """
        Allows manual painting using keyboard controls in a curses window.

        Args:
            stdscr (curses.window): Standard screen for curses.
        """
        posX, posY = 0, 0
        self.move('x', posX)
        self.move('y', posY)

        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)

        self.laser_controller.switch_laser('on')

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
                # Assigning posX and posY to the left column of the grid
                for row in range(3):
                    self.calibration_grid[row, 0, 0] = posX
                    self.calibration_grid[0, row, 1] = posY
            elif key == ord('c'):
                # Assigning posX and posY to the right column of the grid
                for row in range(3):
                    self.calibration_grid[row, 2, 0] = posX
                    self.calibration_grid[2, row, 1] = posY
            elif key == ord('q'):
                break

            self.move('x', posX)
            self.move('y', posY)

        self.laser_controller.switch_laser('off')
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def interpolate_calibration_grid(self, verbose=False):
        """
        Interpolates the middle row and column of the calibration grid.

        Args:
            verbose (bool): If True, prints the interpolated grid values.
        """
        for i in range(3):
            self.calibration_grid[1, i, 1] = (self.calibration_grid[0, i, 1] + self.calibration_grid[2, i, 1]) / 2
            self.calibration_grid[i, 1, 0] = (self.calibration_grid[i, 0, 0] + self.calibration_grid[i, 2, 0]) / 2

        if verbose:
            for i in range(3):
                print(" ".join(str(self.calibration_grid[i, j, 0]) for j in range(3)))
            print()
            for i in range(3):
                print(" ".join(str(self.calibration_grid[i, j, 1]) for j in range(3)))

    def run_calibration_test(self):
        """
        Tests the calibration by moving the laser to each point in the calibration grid.
        """
        for i in range(3):
            for j in range(3):
                self.laser_controller.switch_laser('on')
                self.move('x', self.calibration_grid[i, j, 0])
                self.move('y', self.calibration_grid[i, j, 1])
                time.sleep(3)
        self.laser_controller.switch_laser('off')

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
    
    painter = LaserPainter(socket_x, socket_y, calx, caly, mcp)  # Adjust as needed

    curses.wrapper(painter.paint_manually)
    painter.interpolate_calibration_grid(verbose=True)
    painter.run_calibration_test()

