import numpy as np
import cv2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from teste import load_calibration_data
from teste import find_tumour

def compute_camera_matrix(intrinsic_matrix, angle, radius=25):
    """
    Compute the camera matrix for a given angle.

    :param intrinsic_matrix: The intrinsic camera matrix.
    :param angle: The rotation angle in degrees.
    :param radius: The radius of the camera's rotation around the object.
    :return: The complete camera matrix.
    """
    # Convert angle to radians
    theta = np.radians(angle)

    # Calculate camera position
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)

    # Camera is looking at the origin, so the direction is the negative of the position
    direction = np.array([0, 0, 0]) - np.array([x, y, 0])
    direction = direction / np.linalg.norm(direction)  # Normalize the direction

    # Define up vector
    up = np.array([0, 0, 1])

    # Compute rotation matrix using look-at formula
    z_axis = direction
    x_axis = np.cross(up, z_axis)
    y_axis = np.cross(z_axis, x_axis)
    rotation_matrix = np.array([x_axis, y_axis, z_axis]).T

    # Compute translation vector
    translation_vector = np.array([x, y, 0])

    # Combine intrinsic and extrinsic parameters
    extrinsic_matrix = np.vstack((rotation_matrix.T, translation_vector)).T
    camera_matrix = intrinsic_matrix @ extrinsic_matrix

    print(camera_matrix)

    return camera_matrix

def visualize_voxel_grid(voxel_grid):
    # print(voxel_grid)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Create the grid for plotting.
    # Note: The grid size is one more than the voxel grid size in each dimension.
    grid_x, grid_y, grid_z = np.indices((voxel_grid.shape[0] + 1, voxel_grid.shape[1] + 1, voxel_grid.shape[2] + 1))

    # Plotting the voxels
    ax.voxels(grid_x, grid_y, grid_z, voxel_grid, facecolors='red', edgecolor='k')

    # Setting the labels
    ax.set_xlabel('X Axis')
    ax.set_ylabel('Y Axis')
    ax.set_zlabel('Z Axis')

    # Display the plot
    plt.show()

def main(intrinsic_matrix):
    # Load silhouette images from the specified folder
    num_images = 360
    image_folder = "images/reconstruction"
    silhouettes = [f'{image_folder}/angle_{i}.jpg' for i in range(num_images)]
    silhouettes = [find_tumour(image)[0] for image in silhouettes]

    # Initialize 3D voxel grid
    grid_size_x, grid_size_y, grid_size_z = 50, 50, 50
    voxel_grid = np.zeros((grid_size_x, grid_size_y, grid_size_z))

    # Compute the visual hull
    for x in range(grid_size_x):
        for y in range(grid_size_y):
            for z in range(grid_size_z):
                voxel = np.array([x, y, z, 1])
                inside_all_silhouettes = True
                for i, silhouette in enumerate(silhouettes):
                    camera_matrix = compute_camera_matrix(intrinsic_matrix, i)
                    # print(f"camera_matrix:{camera_matrix} and voxel:{voxel}")
                    projected_point = camera_matrix @ voxel
                    print(projected_point)
                    px, py = projected_point[:2] / projected_point[2]
                    projected_x, projected_y = int(px), int(py)
                    if (projected_x, projected_y) not in silhouette:
                        inside_all_silhouettes = False
                        break
                if inside_all_silhouettes:
                    voxel_grid[x, y, z] = 1

    # Visualize the voxel grid
    visualize_voxel_grid(voxel_grid)

if __name__=="__main__":
    # Example usage
    intrinsic_matrix = load_calibration_data()[0]
    intrinsic_matrix[0,2] -= 130
    intrinsic_matrix[1,2] -= 65
    main(intrinsic_matrix)


