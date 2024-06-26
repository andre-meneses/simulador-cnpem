import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from collections import defaultdict

class Tumour:
    """
    A class representing a tumour in 3D space.

    Attributes:
        coordinates (numpy.ndarray): The coordinates of the tumour vertices.
        cx (float): The x-coordinate of the center of the tumour.
        cy (float): The y-coordinate of the center of the tumour.
        rotation (float): The rotation angle of the tumour around the y-axis.
        T_origin (numpy.ndarray): Transformation matrix for translating to the origin.
        T_back (numpy.ndarray): Transformation matrix for translating back to the original position.
    """

    def __init__(self, coordinates, center):
        """
        Initialize the Tumour object.

        Args:
            coordinates (numpy.ndarray): The coordinates of the tumour vertices.
            center (tuple): The center coordinates of the tumour.
        """
        rotation_matrix_x = np.array([[1,0,0],[0, 0, -1],[0, 1, 0]])
        rotation_matrix_y = np.array([[1,0,0],[0, 1, 0],[0, 0, 1]])

        self.cx = center[0]
        self.cy = center[1]
        self.coordinates = np.dot(rotation_matrix_x.T, coordinates.T).T
        self.coordinates = np.dot(rotation_matrix_y.T, self.coordinates.T).T
        self.rotation = 0

        self.T_origin = np.array([[1, 0, 0, -self.cx], [0,1,0, -self.cy], [0,0,1,0], [0,0,0,1]])
        self.T_back = np.array([[1, 0, 0, self.cx], [0,1,0, self.cy], [0,0,1,0], [0,0,0,1]])

        for i,coord in enumerate(self.coordinates):
            self.coordinates[i,1]  = 209 - self.coordinates[i,1]

    def rotate_tumour(self, theta):
        """
        Rotate the tumour around the y-axis.

        Args:
            theta (float): The angle of rotation in degrees.
        """
        self.rotation = theta
        theta = np.deg2rad(theta)
        R_y = np.array([[np.cos(theta), 0, np.sin(theta),0],[0, 1, 0, 0],[-np.sin(theta), 0, np.cos(theta),0], [0,0,0,1]])
        transformation_matrix = self.T_back @ R_y @ self.T_origin
        vertices_homogeneous = np.column_stack((self.coordinates, np.ones(len(self.coordinates))))
        vertices_transformed = (transformation_matrix @ vertices_homogeneous.T).T
        self.coordinates = vertices_transformed[:, :3]

    def sanity_plot(self):
        """
        Plot the tumour in 3D space.
        """
        x = self.coordinates[:,0]
        y = self.coordinates[:,1]
        z = self.coordinates[:,2]

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlabel('X-axis')
        ax.set_ylabel('Y-axis')
        ax.set_zlabel('Z-axis')
        ax.plot(x,y,z)
        plt.show()

    def plot_slices(self):
        """
        Plot the slices of the tumour.
        """
        transformed_list = self.generate_slices()
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        i = 0
        for key,item in transformed_list.items():
            x = [it[0] for it in item]
            y = [it[1] for it in item]
            ax.scatter(x, y, np.full_like(x,int(key)))
        ax.set_xlabel('X-axis')
        ax.set_ylabel('Y-axis')
        ax.set_zlabel('Z-axis')
        ax.legend()
        plt.show()

    def generate_slices(self, num_slices=15, tolerance=20):
        """
        Generate slices of the tumour.

        Args:
            num_slices (int, optional): Number of slices to generate. Defaults to 15.
            tolerance (int, optional): Tolerance for considering a point in a slice. Defaults to 20.

        Returns:
            dict: A dictionary containing slices of the tumour.
        """
        ordered_points = sorted(self.coordinates, key=lambda xyz: (xyz[2], xyz[1], xyz[0]))
        min_z, max_z = ordered_points[0][2], ordered_points[-1][2]
        slices = defaultdict(list)
        z_list = np.linspace(min_z, max_z, num_slices)

        for point in ordered_points:
            for z in z_list:
                if abs(point[2] - z) <= tolerance:
                    slices[z].append([point[0], point[1]])
                    break

        for z_value, xy_list in slices.items():
            slices[z_value] = sorted(xy_list, key=lambda xy: (xy[1], xy[0]))

        return slices

if __name__=="__main__":

    coords = np.load('data/coordinates.npy')
    center = np.load('data/center.npy')
    tumor = Tumour(coords, center)
    tumor.rotate_tumour(36)
    # tumor.sanity_plot()
    # tumor.generate_slices()
    tumor.plot_slices()
