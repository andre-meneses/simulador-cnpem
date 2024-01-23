import serial
import numpy as np
import curses
from Camera import Camera
from Image_processor import ImageProcessor
from teste import find_contour
import matplotlib.pyplot as plt
from outils import show_wait_destroy
import time
import os
import cv2 as cv

class GoniometerController:
    def __init__(self, port='/dev/ttyUSB0', baud_rate=115200):
        self.port = port
        self.baud_rate = baud_rate
        self.steps_per_degree = 12800  # Assuming 12800 steps per degree
        self.ser = serial.Serial(self.port, self.baud_rate)

    def __enter__(self):
        self.ser = serial.Serial(self.port, self.baud_rate)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.ser.close()

    def _parse_state(self, message):
        message = message.decode('utf-8').strip()
        return int(message[0])

    def _prepare(self):
        self.ser.write(b'SHH\r\n')       
        self.ser.write(b'MTH = -2\r\n')  
        self.ser.write(b'CN1\r\n')       

    def move(self, angle, speed=60000, acc=5000, dec=5000, verbose=False):
        self._prepare()
        angle_steps = str(int(angle * self.steps_per_degree))
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


    def move_manually(self,stdscr):
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)

        while True:
            stdscr.clear()
            stdscr.refresh()

            key = stdscr.getch()
            movement = 0.15

            if key == curses.KEY_LEFT:
                self.move(-1)
            elif key == curses.KEY_RIGHT:
                self.move(1)
            elif key == ord('q'):
                break

        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def calibrate_coordinates(self, camera):
        angle = 0

        angle_areas = []

        for i in range(50):
            area = find_contour(i, camera)
            angle_areas.append([angle,area])
            self.move(0.1)
            print(i)
            angle += 0.1

        self.move(-5)

        angle = 0

        for i in range(50):
            area = find_contour(i*-1, camera)
            angle_areas.append([angle,area])
            self.move(-0.1)
            print(i*-1)
            angle -= 0.1

        angle_areas = np.array(angle_areas)
        max_index = np.argmax(angle_areas[:,1])
        mpoint = angle_areas[max_index]

        self.move(5)

        print(f"Max area:{mpoint[1]}, angle:{mpoint[0]}")
        self.move(mpoint[0])
        return mpoint[0]

    def construct_3d_model(self):
        camera = Camera(0)

        # for i in range(360):
            # camera.take_picture(f"images/reconstruction/angle_{i}.jpg")
            # self.move(1)
        
        dataset_dir = "images/reconstruction"
        images = []

        for i in range(360):
            img_path = os.path.join(dataset_dir, f"angle_{i}.jpg")
            img = cv.imread(img_path, cv.IMREAD_GRAYSCALE)[65:250,130:500]
            images.append(img)
            # show_wait_destroy('a',img)

        depth_maps = []
        stereo = cv.StereoBM_create(numDisparities=16, blockSize=15)

        for img in images:
            disparity = stereo.compute(img, img)
            disparity_normalized = cv.normalize(disparity, None, 0, 255, cv.NORM_MINMAX, cv.CV_8U)
            # Append the normalized disparity map to the list of depth maps
            depth_maps.append(disparity_normalized)

        # Visualize all the depth maps

        sum_depth_map = np.zeros_like(depth_maps[0], dtype=np.float64)

        # Compute the sum of all depth maps

        for depth_map in depth_maps:
            sum_depth_map += depth_map.astype(np.float64)

        # Calculate the mean depth map by dividing the sum by the number of depth maps
        mean_depth_map = (sum_depth_map / len(depth_maps)).astype(np.uint8)
        # Display the mean depth map

        plt.figure(figsize=(8, 6))
        plt.imshow(mean_depth_map, cmap='jet')
        plt.title('Mean Depth Map')
        plt.axis('off')
        plt.show() 

if __name__ == '__main__':
    with GoniometerController() as controller:
        # controller.ser.write(b'ST\r\n')
        # controller.move(-90)
        # angle1 = controller.calibrate_coordinates(0)
        # time.sleep(30)
        # controller.move(90)
        # angle2 = controller.calibrate_coordinates(2)
        # print(90 + angle2)
         
        # Ângulo entre camêras: 89° 
        # controller.move(-89)
        controller.construct_3d_model()

