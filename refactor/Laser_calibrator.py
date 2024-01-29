import socket
import pickle
import Mcp
from Camera import Camera
from Image_processor import ImageProcessor
import numpy as np
import time
from Goniometer import GoniometerController
from Tumour import Tumour

class LaserCalibrator:
    def __init__(self, x_socket, y_socket, x_cal_factor, y_cal_factor, mcp_controller):
        self.x_socket = x_socket
        self.y_socket = y_socket
        self.x_calibration_factor = x_cal_factor
        self.y_calibration_factor = y_cal_factor
        self.mcp_controller = mcp_controller
        self.calibration_grid = np.zeros((3, 3, 2))
        self.fine_grid = np.zeros((3, 3, 2))
        self.green_map = []

    def initial_grid(self, stdscr):
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
                for row in range(3):
                    self.calibration_grid[row, 0, 0] = posX
                    self.calibration_grid[0, row, 1] = posY
            elif key == ord('c'):
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
       self.whole_green_map = []

    def run_calibration_test(self, fine_tune=False):
        camera = Camera(2)
        for i in range(3):
            for j in range(3):
                self.laser_controller.switch_laser('on')
                self.move('x', calibration_grid[i, j, 0])
                self.move('y', calibration_grid[i, j, 1])
                camera.take_picture(f"images/calibration/brgt/laser_avg_{i}{j}.jpg")
                time.sleep(3)
        self.laser_controller.switch_laser('off')

    def fine_tune_calibration(self):
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
                print(f"Green map: {self.green_map}")
                print(f"Fine_grid: {self.fine_grid[i,j]}")
                print()
                self.green_map = []
                time.sleep(2)

    def save_calibration_data(self, filename="data/calibration_data.pkl"):
        with open(filename, "wb") as file:
            pickle.dump({'calibration_grid': self.calibration_grid, 'fine_grid': self.fine_grid}, file)

    def load_calibration_data(self, filename="data/calibration_data.pkl"):
        with open(filename, "rb") as file:
            data = pickle.load(file)
            self.calibration_grid = data['calibration_grid']
            self.fine_grid = data['fine_grid']

    def calibration_routine(self):
        with GoniometerController() as controller:
            controller.calibrate_coordinates(0)
            self.compute_centroids(camera_number=2)
            self.load_calibration_data()
            self.fine_tune_calibration()
            self.save_calibration_data()
            controller.move(-89)
            self.compute_centroids()
