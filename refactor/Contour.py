import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from teste import find_tumour
import pyvista as pv
from teste import show_wait_destroy

class SilhouetteTo3D:
    def __init__(self):
        self.points = []
        self.points_cloud = []

    def find_center(self, contour):
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            self.cx = cx
            self.cy = cy
        else:
            self.cx = 0
            self.cy = 0

    def radius(self, point):
        return point[0] - self.cx

    def add_silhouette(self, contour, theta):
        x = []
        y = []
        for point in contour:
            # print(point)
            # print(point[0])
            self.find_center(contour)
            x = point[0][0]
            y = point[0][1]
            # plt.plot([point[0][0], point[0][1]], [self.cx, self.cy])
            self.points.append([self.radius(point[0]), np.deg2rad(theta), 186 - point[0][1]])

        # plt.plot(x,y)
        # plt.show()

    def cyl2cart(self, point):
        x = point[0] * np.cos(point[1]) 
        y = point[0] * np.sin(point[1]) 
        z = point[2] 

        return [x,y,z]
         
    def convert_coordinates(self):
        for point in self.points:
            point_1 = self.cyl2cart(point)
            self.points_cloud.append(point_1)

    def plot_cloud(self):
        fig = plt.figure()
        # Add a 3D subplot
        ax = fig.add_subplot(111, projection='3d')
        # Scatter plot
        x = [point[0] for point in self.points_cloud]
        y = [point[1] for point in self.points_cloud]
        z = [point[2] for point in self.points_cloud]

        ax.plot(x,y,z)
        plt.show()

    def plot_shell(self):
        cloud = pv.PolyData(np.array(self.points_cloud))
        cloud.plot()

        volume = cloud.delaunay_3d(alpha=2.)
        shell = volume.extract_geometry()
        shell.plot()

if __name__ == "__main__":

    # img_index = [i for i in range(90)] + [j for j in range(270,360)]
    img_index = [i for i in range(180)] 
    image_folder = "images/reconstruction"
    images = [f'{image_folder}/angle_{i}.jpg' for i in img_index]
    contours = [find_tumour(image)[3] for image in images]
    contours = [max(contour, key=cv2.contourArea) for contour in contours]

    s23 = SilhouetteTo3D() 

    for i,contour in enumerate(contours):
        # print(i)
        s23.add_silhouette(contour, i)
    
    s23.convert_coordinates()
    s23.plot_shell()
    # s23.plot_cloud()


