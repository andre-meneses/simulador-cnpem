import socket
import pickle
import Mcp
from Camera import Camera
from Image_processor import ImageProcessor
import numpy as np
import time
from Goniometer import GoniometerController
from Tumour import Tumour
from Laser_calibrator import LaserCalibrator

class LaserPainter:
    def __init__(self, x_socket, y_socket, mcp_controller):
        self.x_socket = x_socket
        self.y_socket = y_socket
        self.mcp_controller = mcp_controller

    def paint_coordinate(self, posX, posY):
        command = f"MWV:{position}\r\n".encode('utf-8')
        (self.x_socket if axis == 'x' else self.y_socket).sendall(command)
    
    def paint_tumour(self, tumour_coordinates, centroid_shift):
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
            for px,volt in zip(pxs, volts):
                x_axis.append([px[0], volt[0]])
                y_axis.append([px[1], volt[1]])

        x_axis = np.array(x_axis)
        y_axis = np.array(y_axis)
        vx = LinearRegression().fit(x_axis[:,0].reshape(-1,1), x_axis[:,1])
        vy = LinearRegression().fit(y_axis[:,0].reshape(-1,1), y_axis[:,1])

        for x,y in tumour_coordinates[::1]:
            xPos = vx.predict(np.array(x).reshape(-1,1))
            yPos = vy.predict(np.array(y).reshape(-1,1))
            self.paint_coordinate(xPos[0],yPos[0])

    def burn_tumour(self, static=False):
        coords = np.load('data/coordinates.npy')
        center = np.load('data/center.npy')
        tumour = Tumour(coords, center)

        with GoniometerController() as controller:
            if not static:
                controller.move(89)
            for i in range(10):
                slices = tumour.generate_slices()
                j = 0

                if not static:
                    self.laser_controller.switch_laser('on')

                for key, value in slices.items():
                    tumour_coordinates = np.array(value)
                    x = tumour_coordinates[:,0]
                    y = tumour_coordinates[:,1]
                    plt.plot(x,y)
                    plt.gca().invert_yaxis()
                    plt.savefig(f"images/planos/plano_{i}_{j}")
                    plt.clf()

                    if not static:
                        self.paint_tumour(tumour_coordinates, (130,65))

                    j += 1

                tumour.rotate_tumour(-36)

                if not static:
                    self.laser_controller.switch_laser('off')
                    controller.move(36)

            if not static:
                controller.move(-89)

if __name__ == '__main__':
    host_x = "192.168.0.11"
    host_y = "192.168.1.10"
    port = 10001
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
    calibrator = LaserCalibrator(socket_x, socket_y, calx, caly, mcp)
    painter = LaserPainter(socket_x, socket_y, mcp)
    calibrator.calibration_routine()
    calibrator.load_calibration_data()
    painter.burn_tumour()
