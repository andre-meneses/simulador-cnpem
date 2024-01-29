import serial
import curses
import numpy as np
from Camera import Camera
from Image_processor import ImageProcessor
from teste import find_contour
import time

class GoniometerController:
    STEPS_PER_DEGREE = 12800
    MOVEMENT_INCREMENT = 0.15

    def __init__(self, port='/dev/ttyUSB0', baud_rate=115200):
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None

    def connect(self):
        self.ser = serial.Serial(self.port, self.baud_rate)

    def disconnect(self):
        if self.ser:
            self.ser.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()
        
    def _parse_state(self, message):
        message = message.decode('utf-8').strip()
        return int(message[0])

    def _prepare_goniometer(self):
        self.ser.write(b'SHH\r\n')
        self.ser.write(b'MTH = -2\r\n')
        self.ser.write(b'CN1\r\n')

    def move(self, angle, speed=60000, acc=5000, dec=5000, verbose=False):
        self._prepare_goniometer()
        angle_steps = str(int(angle * self.STEPS_PER_DEGREE))
        commands = [
            f'PRH={angle_steps}\r\n',
            f'SPH={speed}\r\n',
            # f'ACH={acc}\r\n',
            # f'DCH={dec}\r\n',
            f'BGH\r\n',
            f'MG _BGH\r\n'
        ]

        for cmd in commands:
            self.ser.write(bytes(cmd, 'utf-8'))

        for _ in range(len(commands) + 3):
            self.ser.readline()

        state = self._parse_state(self.ser.readline())
        while state == 1:
            self.ser.write(b'MG _BGH\r\n')
            self.ser.readline()
            state = self._parse_state(self.ser.readline())
            if verbose:
                print(state)

    def calibrate_goniometer(self, camera):
        angle = 0
        angle_areas = []

        try:
            for i in range(50):
                area = find_contour(i, camera)
                angle_areas.append([angle, area])
                self.move(self.MOVEMENT_INCREMENT)
                print(i)
                angle += self.MOVEMENT_INCREMENT

            self.move(-5)

            angle = 0

            for i in range(50):
                area = find_contour(i * -1, camera)
                angle_areas.append([angle, area])
                self.move(-self.MOVEMENT_INCREMENT)
                print(i * -1)
                angle -= self.MOVEMENT_INCREMENT

            angle_areas = np.array(angle_areas)
            max_index = np.argmax(angle_areas[:, 1])
            mpoint = angle_areas[max_index]

            self.move(5)

            print(f"Max area:{mpoint[1]}, angle:{mpoint[0]}")
            self.move(mpoint[0])
            return mpoint[0]
        except Exception as e:
            print(f"Error during calibration: {e}")
            # Handle or log the exception as needed

    def perform_tomography(self):

        camera = Camera(0)

        try:
            for i in range(360):
                camera.take_picture(f"images/reconstruction/angle_{i}.jpg")
                self.move(1)
        except Exception as e:
            print(f"Error during tomography: {e}")
            # Handle or log the exception as needed

if __name__ == '__main__':
    with GoniometerController() as controller:
        controller.connect()
        controller.perform_tomography()
        controller.disconnect()

