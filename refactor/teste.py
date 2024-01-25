import cv2 as cv
from Camera import Camera
from Image_processor import ImageProcessor
import numpy as np
from sklearn.linear_model import LinearRegression
import socket
import matplotlib.pyplot as plt
import Mcp
import glob
import pickle

from outils import show_wait_destroy

def find_contour(index, camera_number):
    camera = Camera(camera_number)
    img = camera.take_picture(return_image=True)[125:250, 150:480]

    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    blurred = cv.GaussianBlur(img_gray, (5, 5), 0)

    ret, thresh = cv.threshold(blurred, 120, 255, cv.THRESH_BINARY)
        
    contours, hierarchy = cv.findContours(image=thresh, mode=cv.RETR_TREE, method=cv.CHAIN_APPROX_SIMPLE)

    # draw contours on the original image
    image_copy = img.copy()
    cv.drawContours(image=image_copy, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv.LINE_AA)

    area = 0

    for contour in contours: 
        area += cv.contourArea(contour)

    # see the results
    # cv.imshow('None approximation', image_copy)
    # cv.waitKey(0)
    cv.imwrite(f"images/contours_teste/camera_{camera_number}_{index}.jpg", image_copy)
    # cv.destroyAllWindows()

    return area


def get_inner_pixels_coordinates(coordinates, image_shape, margin_percent=10):
    # Calculate margin in pixels
    margin_x = int(image_shape[1] * margin_percent / 100)
    margin_y = int(image_shape[0] * margin_percent / 100)

    # Define the contour region
    x_min, y_min = margin_x, margin_y
    x_max, y_max = image_shape[1] - margin_x, image_shape[0] - margin_y

    # Filter coordinates within the contour region
    filtered_coords = [coord for coord in coordinates if x_min <= coord[0] <= x_max and y_min <= coord[1] <= y_max]

    return filtered_coords

def find_tumour(image=None):

    if image is None:
        camera = Camera(0)
        image = camera.take_picture(return_image=True)[65:275,130:500]
    else:
        image = cv.imread(image)[65:275,130:500]

    img_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    blurred = cv.GaussianBlur(img_gray, (5, 5), 0)

    ret, thresh = cv.threshold(blurred, 120, 255, cv.THRESH_BINARY)
        
    contours, hierarchy = cv.findContours(image=thresh, mode=cv.RETR_TREE, method=cv.CHAIN_APPROX_SIMPLE)

    height, width = image.shape[:2]

    # Create a blank mask
    mask = np.zeros((height, width), dtype=np.uint8)

    # Draw the filled contour on the mask
    cv.drawContours(mask, contours, -1, (255), thickness=cv.FILLED)

    img = 255 - thresh
    contours_aa, hierarchy = cv.findContours(image=img, mode=cv.RETR_TREE, method=cv.CHAIN_APPROX_SIMPLE)

    cv.drawContours(image, contours_aa, -1, (255), thickness=cv.FILLED)

    # show_wait_destroy('a', image)

    # Find the pixels inside the contour
    y, x = np.where(mask == 0)

    # Combine x and y into a single array of coordinates
    inside_contour_coordinates = list(zip(x, y))

    sorted_coordinates = sorted(inside_contour_coordinates, key=lambda coord: (coord[1], coord[0]))

    # show_wait_destroy('img_init',mask)

    # coordinates = get_inner_pixels_coordinates(sorted_coordinates, image.shape[:2])

    return sorted_coordinates, (130,65), image, contours_aa

if __name__ == '__main__':
    # find_contour(2, 2)
    # host_x = "192.168.0.11"  # Server's IP address
    # host_y = "192.168.1.10"  # Server's IP address

    # port = 10001  # Port used by the server

    # socket_x = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # socket_y = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # try:
    #     socket_x.connect((host_x, port))
    #     socket_y.connect((host_y, port))
    # except socket.error as e:
    #     print(f"Error connecting to socket: {e}")

    # mcp = Mcp.Mcp()
    # calx = 20 / (113.41 + 114.21)
    # caly = 20 / (153.02 + 154.22)
    
    # controller = GoniometerController()
    # controller.move(89)

    # painter = LaserPainter(socket_x, socket_y, calx, caly, mcp)  # Adjust as needed
    
    # painter.load_calibration_data()

    # find_tumour(painter)

    #-----------------------------------------------------------------------------------------
    # Calibrate camera and save data
    camera_matrix, distortion_coefficients = calibrate_camera("images/camera_calibration")

    save_calibration_data(camera_matrix, distortion_coefficients)

    # Load calibration data
    loaded_camera_matrix, loaded_distortion_coefficients = load_calibration_data()

    print("Loaded Camera Matrix:\n", loaded_camera_matrix)
    print("Loaded Distortion Coefficients:\n", loaded_distortion_coefficients)


