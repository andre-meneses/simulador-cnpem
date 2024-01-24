import numpy as np
import cv2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def plot_voxels(voxels, occupancy, threshold=0.5):
    """
    Plot voxels with occupancy greater than a specified threshold.

    :param voxels: Numpy array of voxel points, shape (N, 3).
    :param occupancy: Numpy array of occupancy values, shape (N,).
    :param threshold: Minimum occupancy value to plot a voxel.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Filter voxels based on the occupancy threshold
    x, y, z = voxels[occupancy > threshold].T

    ax.scatter(x, y, z, c='b', marker='o')
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    plt.title('3D Voxel Plot')
    plt.show()

def sort_centroids(centroids):
    # Sort centroids by y-coordinate
    sorted_by_y = sorted(centroids, key=lambda k: k[1])

    # Sort each batch of three centroids by x-coordinate
    sorted_batches = [sorted(sorted_by_y[i:i + 3], key=lambda k: k[0]) for i in range(0, len(sorted_by_y), 3)]

    sorted_batches_centroids = [(sorted_batches[i][j][0],sorted_batches[i][j][1]) for i in range(len(sorted_batches)) for j in range(3)]

    sorted_batches_contours = [(sorted_batches[i][j][2]) for i in range(len(sorted_batches)) for j in range(3)]

    # Flatten and reshape into a 3x3x2 array
    return np.array([c for batch in sorted_batches_centroids for c in batch]).reshape(3, 3, 2), sorted_batches_contours

# def show_wait_destroy(winname, img):
#     cv.imshow(winname, img)
#     cv.moveWindow(winname, 500, 0)
#     cv.waitKey(0)
#     cv.destroyWindow(winname)


def show_wait_destroy(winname, img):
    # Check if the image has 3 channels (color image)
    if len(img.shape) == 3:
        # Convert color from BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Otherwise, it's a grayscale image and no conversion is needed

    plt.imshow(img, cmap='gray' if len(img.shape) == 2 else None)
    plt.title(winname)
    plt.show()

