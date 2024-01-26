import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from collections import defaultdict

class Tumour:
    def __init__(self, coordinates, center):
        rotation_matrix = np.array([[1,0,0],[0, 0, -1],[0, 1, 0]])
        self.cx = center[0]
        self.cy = center[1]
        self.coordinates = np.dot(rotation_matrix.T, coordinates.T).T
        self.rotation = 0

        self.T_origin = np.array([[1, 0, 0, -self.cx], [0,1,0, -self.cy], [0,0,1,0], [0,0,0,1]])
        self.T_back = np.array([[1, 0, 0, self.cx], [0,1,0, self.cy], [0,0,1,0], [0,0,0,1]])

        for i,coord in enumerate(self.coordinates):
            self.coordinates[i,1]  = 209 - self.coordinates[i,1]

    def rotate_tumour(self, theta):

        self.rotation = theta

        theta = np.deg2rad(theta)

        R_y = np.array([[np.cos(theta), 0, np.sin(theta),0],[0, 1, 0, 0],[-np.sin(theta), 0, np.cos(theta),0], [0,0,0,1]])

        transformation_matrix = self.T_back @ R_y @ self.T_origin

        vertices_homogeneous = np.column_stack((self.coordinates, np.ones(len(self.coordinates))))

        # Apply the transformation
        vertices_transformed = (transformation_matrix @ vertices_homogeneous.T).T

        # Remove homogeneous coordinate
        self.coordinates = vertices_transformed[:, :3]


    def sanity_plot(self):

        # x = self.coordinates[:,0]
        # y = self.coordinates[:,1]
        # z = self.coordinates[:,2]

        # self.coordinates = self.rotate_tumour(90)

        x = self.coordinates[:,0]
        y = self.coordinates[:,1]
        z = self.coordinates[:,2]

        fig = plt.figure()
        # Add a 3D subplot
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlabel('X-axis')
        ax.set_ylabel('Y-axis')
        ax.set_zlabel('Z-axis')
        # Scatter plot

        ax.plot(x,y,z)
        plt.show()

    def plot_slices(self):
        transformed_list = self.generate_slices()

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        for pairs,z in transformed_list:
            # print(pairs)
            x, y = pairs.T
            ax.scatter(x, y, np.full_like(x,z), label=f"z = {z}")

        ax.set_xlabel('X-axis')
        ax.set_ylabel('Y-axis')
        ax.set_zlabel('Z-axis')
        ax.legend()
        plt.show()

    def generate_slices(self):
        ordered_points = sorted(self.coordinates, key=lambda xyz: (xyz[2], xyz[1], xyz[0]))

        slices = defaultdict(list)

        for point in ordered_points:
            slices[point[2]].append([point[0], point[1]])

        # sorted_points = self.coordinates[self.coordinates[:, 2].argsort()]
        # xy_pairs = sorted_points[:, [0, 1]]
        # z_values = sorted_points[:, 2]
        # transformed_list = [(xy_pairs[z_values == z], z) for z in np.unique(z_values)]
        # transformed_array = np.array([(pairs, z) for pairs,z in transformed_list], dtype=object)

        # for i, line in enumerate(transformed_array):
            # transformed_array[i,0] = sorted(line[0], key=lambda xy: (xy[1], xy[0])) 
            # print(transformed_array[i,0])
        
        # return np.array(transformed_array[::10])
        return slices


if __name__=="__main__":

    coords = np.load('data/coordinates.npy')
    center = np.load('data/center.npy')
    tumor = Tumour(coords, center)
    # tumor.sanity_plot()
    tumor.generate_slices()
    # tumor.plot_slices()
