import cv2 as cv
from Camera import Camera
from Image_processor import ImageProcessor
import numpy as np
from sklearn.linear_model import LinearRegression
import socket
import matplotlib.pyplot as plt
import Mcp
from Goniometer import GoniometerController
# from Painter import LaserPainter
# from Socket_Connection import SocketConnection


def show_wait_destroy(winname, img):
    cv.imshow(winname, img)
    cv.moveWindow(winname, 500, 0)
    cv.waitKey(0)
    cv.destroyWindow(winname)

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

def find_tumour():

    camera = Camera(0)
    image = camera.take_picture(return_image=True)[55:390,130:500]

    # centroids = np.array([[153,142], [314,131], [474,124], [157, 258], [321,248
    # ],[482,238],[164,374],[328,365],[489,354]])

    # for center in centroids:
        # center[0] -= 130
        # center[1] -= 55

    # centroids = np.reshape(centroids, (3,3,2))

    # color = (0, 255, 0)  # Green color
    # thickness = 2

    # for center in centroids:
        # cv.circle(image, center, 30, color, thickness)

    img_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    blurred = cv.GaussianBlur(img_gray, (5, 5), 0)

    ret, thresh = cv.threshold(blurred, 120, 255, cv.THRESH_BINARY)
        
    contours, hierarchy = cv.findContours(image=thresh, mode=cv.RETR_TREE, method=cv.CHAIN_APPROX_SIMPLE)

    # draw contours on the original image
    image_copy = image.copy()

    # cv.drawContours(image=image_copy, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv.LINE_AA)

    height, width = image.shape[:2]

    # Create a blank mask
    mask = np.zeros((height, width), dtype=np.uint8)

    # Draw the filled contour on the mask
    cv.drawContours(mask, contours, -1, (255), thickness=cv.FILLED)

    # Find the pixels inside the contour
    y, x = np.where(mask == 255)

    # Combine x and y into a single array of coordinates
    inside_contour_coordinates = list(zip(x, y))

    sorted_coordinates = sorted(inside_contour_coordinates, key=lambda coord: (coord[1], coord[0]))

    return sorted_coordinates, (130,55)

    # x_axis = []
    # y_axis = []

    # voltages = painter.fine_grid

    # # print(voltages)
    # # print(centroids)

    # for pxs, volts in zip(centroids, voltages):
    #     for px,volt in zip(pxs, volts):
    #         # print(px)
    #         # print(volt)
    #         x_axis.append([px[0], volt[0]])
    #         y_axis.append([px[1], volt[1]])

    # # print(x_axis)
    # x_axis = np.array(x_axis)
    # y_axis = np.array(y_axis)

    # vx = LinearRegression().fit(x_axis[:,0].reshape(-1,1), x_axis[:,1])
    # vy = LinearRegression().fit(y_axis[:,0].reshape(-1,1), y_axis[:,1])
    
    # controller = GoniometerController()
    # controller.move(-89)

    # for x,y in sorted_coordinates[::20]:
    #     # print(x)
    #     xPos = vx.predict(np.array(x).reshape(-1,1))
    #     yPos = vy.predict(np.array(y).reshape(-1,1))

    #     # print(xPos)

    #     painter.paint_coordinate(xPos[0],yPos[0])

    # # show_wait_destroy('img_init',mask)

if __name__ == '__main__':
    # find_contour(2, 2)
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
    
    controller = GoniometerController()
    controller.move(89)

    painter = LaserPainter(socket_x, socket_y, calx, caly, mcp)  # Adjust as needed
    
    painter.load_calibration_data()

    find_tumour(painter)
   
