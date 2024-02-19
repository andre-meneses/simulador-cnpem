import serial
import numpy as np
from Image_processor import ImageProcessor
from Camera import Camera

class GoniometerController:
    """
    A class to control a goniometer device for tomography experiments.

    Attributes:
        STEPS_PER_DEGREE (int): The number of steps per degree for the goniometer.
        MOVEMENT_INCREMENT (float): The angle increment for movement in degrees.
        port (str): The port to which the goniometer device is connected.
        baud_rate (int): The baud rate for serial communication with the device.
        ser (serial.Serial): The serial connection object.
        processor (ImageProcessor): An instance of ImageProcessor for image processing.
    """

    STEPS_PER_DEGREE = 12800
    MOVEMENT_INCREMENT = 0.15

    def __init__(self, port='/dev/ttyUSB0', baud_rate=115200):
        """
        Initializes the GoniometerController with default port and baud rate settings.

        Args:
            port (str): The port to which the goniometer device is connected (default is '/dev/ttyUSB0').
            baud_rate (int): The baud rate for serial communication with the device (default is 115200).
        """
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None
        self.processor = ImageProcessor()

    def connect(self):
        """
        Connects to the goniometer device via serial communication.
        """
        self.ser = serial.Serial(self.port, self.baud_rate)

    def disconnect(self):
        """
        Disconnects from the goniometer device.
        """
        if self.ser:
            self.ser.close()

    def __enter__(self):
        """
        Allows using the GoniometerController in a 'with' statement for automatic connection management.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Ensures disconnection from the goniometer device when exiting a 'with' statement.
        """
        self.disconnect()

    def _parse_state(self, message):
        """
        Parses the state message received from the goniometer device.

        Args:
            message (bytes): The message received from the device.

        Returns:
            int: The parsed state value.
        """
        message = message.decode('utf-8').strip()
        return int(message[0])

    def _prepare_goniometer(self):
        """
        Prepares the goniometer device for movement.
        """
        self.ser.write(b'SHH\r\n')
        self.ser.write(b'MTH = -2\r\n')
        self.ser.write(b'CN1\r\n')

    def move(self, angle, speed=60000, acc=5000, dec=5000, verbose=False):
        """
        Moves the goniometer to the specified angle.

        Args:
            angle (float): The target angle in degrees.
            speed (int): The movement speed in steps per second (default is 60000).
            acc (int): The acceleration in steps per second squared (default is 5000).
            dec (int): The deceleration in steps per second squared (default is 5000).
            verbose (bool): If True, prints verbose output during movement (default is False).
        """
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

    def calibrate_goniometer(self, camera, verbose=False):
        """
        Calibrates the goniometer device using image processing.

        Args:
            camera (Camera): The camera object for capturing images.

        Returns:
            float: The calibrated angle for maximum area.
        """
        angle = 0
        angle_areas = []

        try:
            print("Adjusting the panels' positioning")
            for i in range(50):
                area = self.processor.find_contour(i, camera)
                angle_areas.append([angle, area])
                self.move(self.MOVEMENT_INCREMENT)
                if verbose:
                    print(i)
                angle += self.MOVEMENT_INCREMENT

            self.move(-5)

            angle = 0

            for i in range(50):
                area = self.processor.find_contour(i * -1, camera)
                angle_areas.append([angle, area])
                self.move(-self.MOVEMENT_INCREMENT)
                if verbose:
                    print(i * -1)
                angle -= self.MOVEMENT_INCREMENT

            angle_areas = np.array(angle_areas)
            max_index = np.argmax(angle_areas[:, 1])
            mpoint = angle_areas[max_index]

            self.move(5)

            if verbose:
                print(f"Max area:{mpoint[1]}, angle:{mpoint[0]}")

            self.move(mpoint[0])

            return mpoint[0]

        except Exception as e:
            print(f"Error during calibration: {e}")
            # Handle or log the exception as needed

    def perform_tomography(self):
        """
        Performs tomography by capturing images at various angles.

        Raises:
            Exception: If an error occurs during the tomography process.
        """
        camera = Camera(0)
        
        input("Turn on light pannel and press enter")
        print("Performing Tomography")

        try:
            for i in range(360):
                camera.take_picture(f"images/reconstruction/angle_{i}.jpg")
                self.move(1)
        except Exception as e:
            print(f"Error during tomography: {e}")
            # Handle or log the exception as needed

        input("Turn off Light Pannel")

if __name__ == '__main__':
    with GoniometerController() as controller:
        controller.connect()
        # controller.perform_tomography()
        controller.move(180)
        controller.disconnect()

