import socket
import itertools
import outils
import pickle
import time
from Laser import LaserController
import Mcp
import curses
import numpy as np
from Camera import Camera
from Image_processor import ImageProcessor
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
 

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
        self.fine_grid = np.zeros((3,3,2)) 

        self.x_socket.sendall(b'UPMODE:NORMAL\r\n')
        self.y_socket.sendall(b'UPMODE:NORMAL\r\n')

        self.contours = None
        self.centroids = np.zeros((3,3,2))



    def move(self, axis, position):
        """
        Moves the laser painter along the specified axis to the given position.

        Args:
            axis (str): The axis along which to move ('x' or 'y').
            position (float): The position to move to.
        """
        command = f"MWV:{position}\r\n".encode('utf-8')
        (self.x_socket if axis == 'x' else self.y_socket).sendall(command)

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

        camera = Camera(2) 

        for i in range(3):
            for j in range(3):
                self.laser_controller.switch_laser('on')
                self.move('x', calibration_grid[i, j, 0])
                self.move('y', calibration_grid[i, j, 1])
                camera.take_picture(f"images/calibration/brgt/laser_avg_{i}{j}.jpg")
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

    def diag_scan(self, center, n_points, coordinate, verbose=True):

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
        x = x_top_left

        while y < y_top_left + 10 * self.y_calibration_factor and x < x_top_left + 10 * self.x_calibration_factor:
            self.move('y', y)
            self.move('x', x)

            processor = ImageProcessor(camera.take_picture(return_image=True))
            green = processor.avg_green()

            if green > greenest_value:
                greenest_value = green
                greenest_position = (x,y)
                camera.take_picture(f"images/calibration/green_diag_{coordinate}.jpg")

            y += y_step
            x += x_step

        self.laser_controller.switch_laser('off')

        if verbose:
            print(f"Greenest value:{greenest_value}")
            print(f"Greenest position:{greenest_position}")

        return greenest_position

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

    # def scan_calibration(self, center, n_points, coordinate, verbose=True):
    #     x_top_left = center[0] - 5 * self.x_calibration_factor
    #     y_top_left = center[1] - 5 * self.y_calibration_factor

    #     max_brght = -10
    #     max_pos = (0,0)

    #     camera = Camera(2) 

    #     centroids = self.centroids

    #     self.laser_controller.switch_laser('on')

    #     # Calculate the step size for x and y movements
    #     x_step = 10 * self.x_calibration_factor / n_points
    #     y_step = 10 * self.y_calibration_factor / n_points

    #     y = y_top_left
    #     i,j = coordinate[0], coordinate[1]

    #     print()

    #     while y < y_top_left + 10 * self.y_calibration_factor:
    #         self.move('y', y)
    #         x = x_top_left

    #         # brightness = []

    #         while x < x_top_left + 10 * self.x_calibration_factor:
    #             self.move('x', x)

    #             processor = ImageProcessor(camera.take_picture(return_image=True))

    #             # brght = processor.compute_brightness(self.contours[3*i + j])
    #             brght = processor.avg_green()

    #             if brght > max_brght:
    #                 max_brgth = brght
    #                 max_pos = (x,y)

    #             x += x_step

    #         if verbose:
    #             print(f"brgth: {max_brgth}, pos: {max_pos}")

    #         y += y_step


    #     self.fine_grid[i,j,0] = max_pos[0]
    #     self.fine_grid[i,j,1] = max_pos[1]

    #     self.laser_controller.switch_laser('off')
        # return brightness

    # def fine_tune_calibration(self):
    #     for i in range(3):
    #         for j in range(3):
    #             x = self.calibration_grid[i,j,0]
    #             y = self.calibration_grid[i,j,1]
    #             self.scan_calibration((x,y), 10, (i,j))
    #             time.sleep(2)


    # def create_heatmap(self, points):
    #    # Convert points to numpy array for easier manipulation
    #     points_array = np.array(points)

    #     # Separate x, y, and values
    #     x_coords = points_array[:, 0]
    #     y_coords = points_array[:, 1]
    #     values = points_array[:, 2]

    #     # Create the KDE plot
    #     plt.figure(figsize=(8, 6))
    #     sns.kdeplot(x=x_coords, y=y_coords, weights=values, cmap="Greens", fill=True)
    #     plt.colorbar(label='Density')
    #     plt.title('Heatmap in Green Scale with Seaborn')
    #     plt.xlabel('X')
    #     plt.ylabel('Y')

    #     plt.show() 

    # def find_max_z(self,points):

    #     # Step 1: Find the maximum value of z
    #     max_z = max(point[2] for point in points)

    #     # Step 2: Filter points with the maximum z value
    #     max_z_points = [point for point in points if point[2] == max_z]

    #     # Step 3: Calculate the center of the region
    #     if len(max_z_points) > 1:
    #         avg_x = sum(point[0] for point in max_z_points) / len(max_z_points)
    #         avg_y = sum(point[1] for point in max_z_points) / len(max_z_points)
    #         return (avg_x, avg_y)
    #     else:
    #         # If there's only one point, return its (x, y) coordinates
    #         return max_z_points[0][:2]

    # def fine_tune_calibration(self):
    #     for i, j in itertools.product(range(3), repeat=2):
    #         coordinates = self.calibration_grid[i, j, :2]
    #         # brightness = self.scan_calibration(coordinates, 10, (i, j))
    #         self.scan_calibration(coordinates, 10, (i, j))
    #         # x_max, y_max = self.find_max_z(brightness)

    #         # self.fine_grid[i,j,0] = x_max
    #         # self.fine_grid[i,j,1] = y_max

    #         # print(f"x:{x_max}, y:{y_max}")
    #         # self.create_heatmap(brightness)

    #         time.sleep(2)


    def save_calibration_data(self, filename="data/calibration_data.pkl"):
        """
        Saves the calibration grid and fine grid to a file.

        Args:
            filename (str): The name of the file to save the data.
        """
        with open(filename, "wb") as file:
            pickle.dump({'calibration_grid': self.calibration_grid, 'fine_grid': self.fine_grid}, file)

    def load_calibration_data(self, filename="data/calibration_data.pkl"):
        """
        Loads the calibration grid and fine grid from a file.

        Args:
            filename (str): The name of the file to load the data from.
        """
        with open(filename, "rb") as file:
            data = pickle.load(file)
            self.calibration_grid = data['calibration_grid']
            self.fine_grid = data['fine_grid']

    def compute_centroids(self):
        camera = Camera(2) 
        image = camera.take_picture(return_image=True)
        image_processor = ImageProcessor(image)
        centroids = image_processor.centroids("images/centroids/marked_centroids.jpg")
        self.centroids, self.contours = outils.sort_centroids(centroids)

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
    # time.sleep(5)
    # painter.fine_tune_calibration()
    # painter.run_calibration_test(fine_tune=True)

    # curses.wrapper(painter.paint_manually)
    # painter.interpolate_calibration_grid(verbose=True)

    # Load calibration data (can be done later or in a different run)

    # painter.compute_centroids()
    painter.load_calibration_data()

    # time.sleep(3)
    # painter.fine_tune_calibration()
    painter.run_calibration_test(fine_tune=True)

    # Save calibration data
    # painter.save_calibration_data()


