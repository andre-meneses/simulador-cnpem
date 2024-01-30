from Painter import LaserPainter
from Mcp import Mcp
from Socket_connection import SocketConnection
from Image_processor import ImageProcessor
from Function_chain import FunctionLinkedList
from Model_generator import SilhouetteTo3D
from Goniometer import  GoniometerController
import yaml
import socket
import sys

class Runner:
    def __init__(self):
        self.mcp = Mcp()

        self._load_data('config/config.yaml')
        self._connect_sockets()
        self._instantiate_painter()

        self.functions_chain = FunctionLinkedList()
        self.functions_chain.add_function(self._calibrate)
        self.functions_chain.add_function(self._wait_user)
        self.functions_chain.add_function(self._execute_tomography)
        self.functions_chain.add_function(self._generate_model)
        self.functions_chain.add_function(self._burn_tumour)

    def _load_data(self, file_path):
        with open(file_path) as f:
            data = yaml.safe_load(f)
            self.host_x = data['host_x']
            self.host_y = data['host_y']
            self.port = data['port']
            self.cal_x = data['cal_x']
            self.cal_y = data['cal_y']

    def _connect_sockets(self):
        self.socket_x = SocketConnection(self.host_x, self.port)
        self.socket_y = SocketConnection(self.host_y, self.port)

        try:
            self.socket_x.connect()
            self.socket_y.connect()
        except socket.error as e:
            print(f"Error connecting to socket: {e}")

    def _instantiate_painter(self):
        self.painter = LaserPainter(self.socket_x, self.socket_y, self.cal_x, self.cal_y, self.mcp)  

    def _calibrate(self, manual=True):
        painter.calibration_routine(manual=manual)

    def _execute_tomography(self):

        with GoniometerController() as controller:
            controller.connect()
            controller.perform_tomography()
            controller.disconnect()

    def _generate_model(self):
        
        img_index = [i for i in range(180)]
        image_folder = "images/reconstruction"
        images = [f'{image_folder}/angle_{i}.jpg' for i in img_index]

        processor = ImageProcessor(None)  # Initialize ImageProcessor with None image

        # Find contours for each image and get the contour with maximum area
        contours = [processor.find_tumour(image)[1] for image in images]

        # SilhouetteTo3D -> s-two-3d -> s23
        s23 = SilhouetteTo3D() 

        for i,contour in enumerate(contours):
            s23.add_silhouette(contour, i)
    
        s23.convert_coordinates()
        s23.generate_solid()

        s23.save_coordinates()

    def _burn_tumour(self):
        self.painter.load_calibration_data()
        self.painter.burn_tumour()

    def _wait_user(self):
        input("Remove calibration plaque, add tumour and press enter")

    def execute(self, func):
        self.functions_chain.execute_functions_from(func)

if __name__=="__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 Run.py <argument>")
        sys.exit(1)

    # Access the argument provided
    argument = sys.argv[1]

    correspondance = {'calibrate':'_calibrate', 'tomography':'_execute_tomography', 'generate-model':'_generate_model', 'burn-tumour':'_burn_tumour'}

    if argument not in correspondance:
        print("Invalid argument, choose from 'calibrate', 'tomography', 'generate-model', 'burn_tumour'")
        sys.exit(1)

    runner = Runner()
    runner.execute(correspondance[argument])
