import socket
import time
from Laser import LaserController
import Mcp
import curses
import numpy as np
from Camera import Camera
from Image_processor import ImageProcessor

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

        self.fine_grid = np.zeros((3,3,2)) 

    def move(self, axis, position):
        """
        Moves the laser painter along the specified axis to the given position.

        Args:
            axis (str): The axis along which to move ('x' or 'y').
            position (float): The position to move to.
        """
        command = f"MWV:{position}\r\n".encode('utf-8')
        (self.x_socket if axis == 'x' else self.y_socket).sendall(command)

    def fill_grid(self):    
        for i in range(3):
            self.calibration_grid[i,0,0] = 5.85
        for i in range(3):
            self.calibration_grid[i,1,0] = 0.675
        for i in range(3):
            self.calibration_grid[i,2,0] = -4.65

        for i in range(3):
            self.calibration_grid[0,i,1] = -5.10
        for i in range(3):
            self.calibration_grid[1,i,1] = -2.25
        for i in range(3):
            self.calibration_grid[2,i,1] = 0.6

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

    def run_calibration_test(self, fine_tune=False):
        """
        Tests the calibration by moving the laser to each point in the calibration grid.
        """
        if fine_tune:
            calibration_grid = self.fine_grid
        else:
            calibration_grid = self.calibration_grid

        for i in range(3):
            for j in range(3):
                self.laser_controller.switch_laser('on')
                self.move('x', calibration_grid[i, j, 0])
                self.move('y', calibration_grid[i, j, 1])
                time.sleep(3)
        self.laser_controller.switch_laser('off')

    def scan_area(self, center, n_points):
        x_top_left = center[0] - 5 * self.x_calibration_factor
        y_top_left = center[1] - 5 * self.y_calibration_factor

        self.move('x', x_top_left)
        self.move('y', y_top_left)

        self.laser_controller.switch_laser('on')

        # Calculate the step size for x and y movements
        x_step = 10 * self.x_calibration_factor / n_points
        y_step = 10 * self.y_calibration_factor / n_points

        y = y_top_left
        while y < y_top_left + 10 * self.y_calibration_factor:
            self.move('y', y)
            x = x_top_left
            while x < x_top_left + 10 * self.x_calibration_factor:
                self.move('x', x)
                x += x_step
            y += y_step

        self.laser_controller.switch_laser('off')

    def scan_grid(self):
        for i in range(3):
            for j in range(3):
                x = self.calibration_grid[i,j,0]
                y = self.calibration_grid[i,j,1]
                self.scan_area((x,y), 100)
                time.sleep(2)

    def scan_calibration(self, center, n_points, coordinate, verbose=True):
        x_top_left = center[0] - 5 * self.x_calibration_factor
        y_top_left = center[1] - 5 * self.y_calibration_factor

        greenest_value = -10
        greenest_position = (0,0)

        camera = Camera(2) 

        self.laser_controller.switch_laser('on')

        # Calculate the step size for x and y movements
        x_step = 10 * self.x_calibration_factor / n_points
        y_step = 10 * self.y_calibration_factor / n_points

        y = y_top_left
        while y < y_top_left + 10 * self.y_calibration_factor:
            self.move('y', y)
            x = x_top_left
            while x < x_top_left + 10 * self.x_calibration_factor:
                self.move('x', x)

                processor = ImageProcessor(camera.take_picture(return_image=True))
                green = processor.avg_green()

                if green > greenest_value:
                    greenest_value = green
                    greenest_position = (x,y)
                    camera.take_picture(f"images/calibration/green_{coordinate}.jpg")
                x += x_step
            y += y_step

        self.laser_controller.switch_laser('off')

        if verbose:
            print(f"Greenest value:{greenest_value}")
            print(f"Greenest position:{greenest_position}")

        self.fine_grid[*coordinate, 0] = greenest_position[0]
        self.fine_grid[*coordinate, 1] = greenest_position[1]


    def fine_tune_calibration(self):
        for i in range(3):
            for j in range(3):
                x = self.calibration_grid[i,j,0]
                y = self.calibration_grid[i,j,1]
                self.scan_calibration((x,y), 10, (i,j))
                time.sleep(2)

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

    # curses.wrapper(painter.paint_manually)
    # painter.interpolate_calibration_grid(verbose=True)
    # time.sleep(10)
    # painter.scan_grid()
    # painter.run_calibration_test()
    # painter.paint_pattern_1()
    painter.fill_grid()
    time.sleep(5)
    painter.fine_tune_calibration()
    painter.run_calibration_test(fine_tune=True)

