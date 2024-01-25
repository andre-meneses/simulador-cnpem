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
        self.coordinates = None

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
            self.find_center(contour)
            x = point[0][0]
            y = point[0][1]
            self.points.append([self.radius(point[0]), np.deg2rad(theta), 186 - point[0][1]])

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

    def generate_solid(self):
        cloud = pv.PolyData(np.array(self.points_cloud))
        surf = cloud.delaunay_3d()
        voxels = pv.voxelize(surf, check_surface=False)
        self.coordinates = np.array(voxels.points)

    def save_coordinates(self, filename='data/coordinates.npy'):
        # Save coordinates to the specified file
        np.save(filename, self.coordinates)

    def load_coordinates(self, filename='data/coordinates.npy'):
        # Load coordinates from the specified file
        self.coordinates = np.load(filename)

    def plot_shell(self, plot_type="Surface"):
        cloud = pv.PolyData(np.array(self.points_cloud))
        surf = cloud.delaunay_3d()

        if plot_type == "Surface":
            surf.plot(show_edges=False)
        else:
            voxels = pv.voxelize(surf, check_surface=False)
            voxels.plot()

    def plot_slices(self):
        sorted_points = self.coordinates[self.coordinates[:, 1].argsort()]
        y_values = sorted_points[:, 1]
        xz_pairs = sorted_points[:, [0, 2]]
        transformed_list = [(y, xz_pairs[y_values == y]) for y in np.unique(y_values)]
        transformed_array = np.array([(y, pairs) for y, pairs in transformed_list], dtype=object)

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        for y, pairs in transformed_list[::5]:
            x, z = pairs.T
            ax.scatter(x, np.full_like(x, y), z, label=f"y = {y}")

        ax.set_xlabel('X-axis')
        ax.set_ylabel('Y-axis')
        ax.set_zlabel('Z-axis')
        ax.legend()
        plt.show()

if __name__ == "__main__":

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
    s23.generate_solid()
    s23.save_coordinates()
    # s23.plot_cloud()


