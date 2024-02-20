import socket
import os
import cv2
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
from sklearn.linear_model import LinearRegression
from Goniometer import GoniometerController
from Tumour import Tumour
from Socket_connection import SocketConnection
 

class LaserPainter:
    """
    Class to control a laser painter device, capable of moving along X and Y axes,
    and controlling a laser for burning the tumour. 

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
        self.green_map = []
        self.whole_green_map = []

        self.x_socket.send_data('UPMODE:NORMAL\r\n')
        self.y_socket.send_data('UPMODE:NORMAL\r\n')

        self.contours = None
        self.centroids = np.zeros((3,3,2))
        self.centroid_shift = None

    def move(self, axis, position):
        """
        Moves the laser painter along the specified axis to the given position.

        Args:
            axis (str): The axis along which to move ('x' or 'y').
            position (float): The position to move to.
        """
        command = f"MWV:{position}\r\n"
        (self.x_socket if axis == 'x' else self.y_socket).send_data(command)

    def paint_coordinate(self, posX, posY):
        """
        Moves the laser to the specified coordinate and activates the laser for painting.

        Args:
            posX (float): X-coordinate to paint.
            posY (float): Y-coordinate to paint.
        """
        posX = posX.item()
        posY = posY.item()

        self.move('x', posX)
        self.move('y', posY)

        # self.laser_controller.switch_laser('on')
        # self.laser_controller.switch_laser('off')

    def set_laser_grid(self, stdscr):
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

    def scan_diagonal(self, center, n_points, coordinate, verbose=False):
        """
        Scans the diagonal area around a given center point.

        Args:
            center (tuple): Center coordinates to start the scan from.
            n_points (int): Number of points to scan along the diagonal.
            coordinate (tuple): Coordinates of the point being scanned.
            verbose (bool): If True, prints scan results.

        Returns:
            tuple: A tuple containing the greenest position and its brightness value.
        """
        greenest_value = -10
        greenest_position = (0,0)

        camera = Camera(2)

        indexes = [2,3,4,5,6,7,8]

        # Calculate the step size for x and y movements
        x_step = 10 * self.x_calibration_factor / n_points
        y_step = 10 * self.y_calibration_factor / n_points

        for i in indexes:
            x_top_left = center[0] - i * self.x_calibration_factor
            y_top_left = center[1] - i * self.y_calibration_factor

            self.laser_controller.switch_laser('on')

            y = y_top_left
            x = x_top_left

            while y < y_top_left + 15 * self.y_calibration_factor and x < x_top_left + 15 * self.x_calibration_factor:
                self.move('y', y)
                self.move('x', x)

                processor = ImageProcessor(camera.take_picture(return_image=True))
                green = processor.compute_brightness(self.contours[3*coordinate[0] + coordinate[1]])

                # self.green_map.append([x,y,gree])
                
                if green >= 254:
                    self.green_map.append([x,y,green])

                self.whole_green_map.append([x,y,green])

                if green > greenest_value:
                    greenest_value = green
                    greenest_position = (x,y)
                    # print((x,y))
                    camera.take_picture(f"images/calibration/green_{coordinate}.jpg")

                y += y_step
                x += x_step

            self.laser_controller.switch_laser('off')

            if verbose:
                print(f"Greenest value:{greenest_value}")
                print(f"Greenest position:{greenest_position}")

        if len(self.green_map) != 0:
            greens = np.array(self.green_map)
            x_values = np.array([coord[0] for coord in greens])
            y_values = np.array([coord[1] for coord in greens])
            return (x_values.mean(), y_values.mean()), greenest_value
        else:
            return greenest_position, greenest_value
    
    def scan_calibration(self, center, n_points, coordinate, verbose=False, line=15, mb=-10):
        """
        Scans a calibration area around a given center point.

        Args:
            center (tuple): Center coordinates to start the scan from.
            n_points (int): Number of points to scan along each axis.
            coordinate (tuple): Coordinates of the point being scanned.
            verbose (bool): If True, prints scan results.
            line (int): Length of the square area to scan.
            mb (int): Initial maximum brightness value.

        Returns:
            int: Maximum brightness value found during the scan.
        """
        x_top_left = center[0] - (line/2) * self.x_calibration_factor
        y_top_left = center[1] - (line/2) * self.y_calibration_factor

        max_brght = mb

        i, j = coordinate[0], coordinate[1]

        max_pos = [self.calibration_grid[i, j, 0], self.calibration_grid[i, j, 1]]

        camera = Camera(2)

        centroids = self.centroids

        self.laser_controller.switch_laser('on')

        # Calculate the step size for x and y movements
        x_step = 10 * self.x_calibration_factor / n_points
        y_step = 10 * self.y_calibration_factor / n_points

        y = y_top_left

        # print()

        while y < y_top_left + line * self.y_calibration_factor:
            self.move('y', y)
            x = x_top_left

            brightness = []

            while x < x_top_left + line * self.x_calibration_factor:
                self.move('x', x)

                processor = ImageProcessor(camera.take_picture(return_image=True))

                brght = processor.compute_brightness(self.contours[3*i + j])
                # brght = processor.avg_green()

                if brght == max_brght:
                    # Add to green_map if brightness equals max_brght
                    self.green_map.append([x, y, brght])
                elif brght > max_brght:
                    # If a new maximum is found, clear the green map
                    # and add the new maximum brightness value
                    self.green_map = [[x, y, brght]]
                    max_brght = brght  # Update max_brght to the new maximum
                    max_pos = (x, y)
                    
                x += x_step

            # print(brightness)

            if verbose:
                print(f"brgth: {max_brght}, pos: {max_pos}")

            y += y_step

        self.laser_controller.switch_laser('off')
        return max_brght

    def fine_tune_calibration(self):
        """
        Fine tunes the calibration by scanning diagonals and calibration areas for each grid point.
        """
        print("Fine tune calibration")
        print("------------------------")
        for i in range(3):
            for j in range(3):
                x = self.calibration_grid[i,j,0]
                y = self.calibration_grid[i,j,1]
                pos_1, gv1 = self.scan_diagonal((x,y), 10, (i,j))
                self.scan_calibration(pos_1, 10, (i,j))

                array = np.array(self.green_map)

                x_values = np.array([coord[0] for coord in array])
                y_values = np.array([coord[1] for coord in array])

                self.fine_grid[i,j,0] = np.mean(x_values)
                self.fine_grid[i,j,1] = np.mean(y_values)

                # print(f"Green map: {self.green_map}")
                # print(f"Fine_grid: {self.fine_grid[i,j]}")
                # print()
                self.green_map = []
                time.sleep(2)
   
    def plot_green_map(self, name):
        """
        Plots the green_map data as a color map.

        Args:
            name (str): Name of the file to save the plot.
        """

        if not self.green_map:
            print("Green map is empty. No data to plot.")
            return

        # Extract x, y, and green values
        x_values = [point[0] for point in self.whole_green_map]
        y_values = [point[1] for point in self.whole_green_map]
        green_values = [point[2] for point in self.whole_green_map]

        # Normalize the green values to the range [0, 1] for color mapping
        norm = mcolors.Normalize(vmin=min(green_values), vmax=max(green_values))

        # Create the scatter plot
        plt.scatter(x_values, y_values, c=green_values, cmap='Greens', norm=norm)
        plt.colorbar()  # Add a color bar to indicate the scale of green values
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.title('Green Map Color Plot')
        plt.savefig(f"{name}", format=pdf)
        # plt.show()

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

    def compute_centroids(self, use_saved_data=False, camera_number=0):
        """
        Computes centroids of marked points in an image.

        Args:
        - use_saved_data (bool): Whether to use saved centroid data.
        - camera_number (int): The camera number.

        Returns:
        - None
        """
        if camera_number == 0:
            if use_saved_data:
                try:
                    with open('data/centroids_data.pkl', 'rb') as file:
                        self.centroids = pickle.load(file)
                    # print("Loaded centroids from file.")
                except (FileNotFoundError, EOFError):
                    print("File not found or empty. Computing centroids instead.")
                    use_saved_data = False

            if not use_saved_data:
                camera = Camera(0)
                image = camera.take_picture(return_image=True)
                image_processor = ImageProcessor(image)
                centroids = image_processor.centroids(f"images/centroids/marked_centroids_image_{camera_number}.jpg")
                self.centroids, self.contours = outils.sort_centroids(centroids)

                if not os.path.exists('data'):
                    os.makedirs('data')
                with open('data/centroids_data.pkl', 'wb') as file:
                    pickle.dump(self.centroids, file)
                # print("Computed and saved centroids.")

        else:
            camera = Camera(2)
            image = camera.take_picture(return_image=True)
            image_processor = ImageProcessor(image)
            centroids = image_processor.centroids(f"images/centroids/marked_centroids_image_{camera_number}.jpg")
            self.centroids, self.contours = outils.sort_centroids(centroids)
            print("Computed centroids camera 2")

    def paint_tumour(self, tumour_coordinates, centroid_shift):
        """
        Paints the tumor on the image.

        Args:
        - tumour_coordinates (array): Array of tumor coordinates.
        - centroid_shift (tuple): Shift of the centroid.

        Returns:
        - None
        """
        x_axis = []
        y_axis = []

        self.load_calibration_data()

        voltages = self.fine_grid

        self.compute_centroids(use_saved_data=True)
        centroids = self.centroids

        for horizontal_line in centroids:
            for center in horizontal_line:
                center[0] -= centroid_shift[0]
                center[1] -= centroid_shift[1]

        for pxs, volts in zip(centroids, voltages):
            for px, volt in zip(pxs, volts):
                x_axis.append([px[0], volt[0]])
                y_axis.append([px[1], volt[1]])

        x_axis = np.array(x_axis)
        y_axis = np.array(y_axis)

        vx = LinearRegression().fit(x_axis[:, 0].reshape(-1, 1), x_axis[:, 1])
        vy = LinearRegression().fit(y_axis[:, 0].reshape(-1, 1), y_axis[:, 1])

        for x, y in tumour_coordinates[::1]:
            xPos = vx.predict(np.array(x).reshape(-1, 1))
            yPos = vy.predict(np.array(y).reshape(-1, 1))

            self.paint_coordinate(xPos[0], yPos[0])

    def calibration_routine(self, manual=False):
        """
        Performs calibration routine.

        Args:
        - manual (bool): Whether to calibrate manually.

        Returns:
        - None
        """
        with GoniometerController() as controller:
            input("Turn on light pannel and press enter")
            controller.calibrate_goniometer(0)

            input("Turn off light pannel and press enter")

            # In order to calibrate laser, compute centroids when facing the laser camera. 
            self.compute_centroids(camera_number=2) 

            if manual:
                print("-----------------------------------------")
                print("Manual Calibration")
                print("Align the beam with the initial orifice and press 'a'. Next, move the beam to the final orifice at coordinates (3,3) and press 'c'. Lastly, press 'q' to complete the process.")
                print("-----------------------------------------")

            if manual:
                curses.wrapper(self.set_laser_grid)
                self.interpolate_calibration_grid(verbose=False)
            else:
                self.load_calibration_data()

            self.fine_tune_calibration()
            self.save_calibration_data()
            controller.move(-89)

            # In order to make the correspondence voltage - pixe, compute centroids when facing the other camera
            self.compute_centroids()

    def burn_tumour(self, static=False, angle_per_step=36):
        """
        Burns the tumor.

        Args:
        - static (bool): Whether the tumor is static.

        Returns:
        - None
        """
        coords = np.load('data/coordinates.npy')
        center = np.load('data/center.npy')

        tumour = Tumour(coords, center)

        with GoniometerController() as controller:
            if not static:
                controller.move(89)

            steps = 360/angle_per_step
            steps = int(steps)

            print("Burning Tumour")
            print("----------------------------")

            for i in range(steps):
                slices = tumour.generate_slices()

                j = 0

                if not static:
                    self.laser_controller.switch_laser('on')

                for key, value in slices.items():

                    tumour_coordinates = np.array(value)
                    x = tumour_coordinates[:, 0]
                    y = tumour_coordinates[:, 1]

                    plt.plot(x, y)
                    plt.gca().invert_yaxis()

                    plt.savefig(f"images/planos/plano_{i}_{j}")
                    plt.clf()

                    if not static:
                        self.paint_tumour(tumour_coordinates, (130, 65))
                    j += 1

                tumour.rotate_tumour(-1*angle_per_step)

                if not static:
                    self.laser_controller.switch_laser('off')
                    controller.move(angle_per_step)

            if not static:
                controller.move(-89)

if __name__ == '__main__':
    host_x = "192.168.0.11"  # Server's IP address
    host_y = "192.168.1.10"  # Server's IP address

    port = 10001  # Port used by the server

    # Create SocketConnection instances
    socket_x = SocketConnection(host_x, port)
    socket_y = SocketConnection(host_y, port)

    try:
        # Connect to the sockets
        socket_x.connect()
        socket_y.connect()
    except socket.error as e:
        print(f"Error connecting to socket: {e}")

    mcp = Mcp.Mcp()
    calx = 20 / (113.41 + 114.21)
    caly = 20 / (153.02 + 154.22)
    
    painter = LaserPainter(socket_x, socket_y, calx, caly, mcp)  # Adjust as needed

    # painter.calibration_routine()
    # painter.run_calibration_test()

    painter.load_calibration_data()
    painter.burn_tumour()

