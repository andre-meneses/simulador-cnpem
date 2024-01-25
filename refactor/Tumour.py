import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class Tumour:
    def __init__(self, coordinates):
        rotation_matrix = np.array([[0, 0, 1],[0, 1, 0],[-1, 0, 0]])
        self.coordinates = np.dot(rotation_matrix, coordinates.T).T

    def rotate_tumour(self, theta):
        theta = np.deg2rad(theta)
        rotation_matrix = np.array([[np.cos(theta), 0, np.sin(theta)],[0, 1, 0],[-np.sin(theta), 0, np.cos(theta)]])
        return np.dot(rotation_matrix, coordinates.T)

    def sanity_plot(self):

        x = self.coordinates[:,0]
        y = self.coordinates[:,1]
        z = self.coordinates[:,2]

        fig = plt.figure()
        # Add a 3D subplot
        ax = fig.add_subplot(111, projection='3d')
        # Scatter plot

        ax.plot(x,y,z)
        plt.show()


if __name__=="__main__":

    coords = np.load('data/coordinates.npy')
    tumor = Tumour(coords)
    tumor.sanity_plot()

