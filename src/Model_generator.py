import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pyvista as pv
from outils import show_wait_destroy
from Image_processor import ImageProcessor

class SilhouetteTo3D:
    """A class for converting 2D silhouettes to 3D point clouds."""

    def __init__(self):
        """Initialize the SilhouetteTo3D object."""
        self.points = []
        self.points_cloud = []
        self.coordinates = None
        self.max_y = 0
        self.max_x = 0
        self.center = False

    def find_center(self, contour):
        """Find the center of the silhouette contour."""
        if self.center == False:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                self.cx = cx
                self.cy = cy
            else:
                self.cx = 0
                self.cy = 0
            self.center = True

    def radius(self, point):
        """Calculate the radius of a point relative to the center."""
        return (point[0] - self.cx)

    def add_silhouette(self, contour, theta):
        """Add a silhouette contour to the point cloud."""
        x = []
        y = []
        for point in contour:
            self.find_center(contour)
            x = point[0][0]
            y = point[0][1]

            self.points.append([self.radius(point[0]), np.deg2rad(theta), 209 - point[0][1] - self.cy])

    def _cyl2cart(self, point):
        """Convert cylindrical coordinates to Cartesian coordinates."""
        x = point[0] * np.cos(point[1]) + self.cx 
        y = point[0] * np.sin(point[1]) 
        z = point[2] + self.cy

        return [x,y,z]
         
    def convert_coordinates(self):
        """Convert cylindrical coordinates of points to Cartesian coordinates."""
        for point in self.points:
            point_1 = self._cyl2cart(point)
            self.points_cloud.append(point_1)

    def plot_cloud(self):
        """Plot the 3D point cloud."""
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        x = [point[0] for point in self.points_cloud]
        y = [point[1] for point in self.points_cloud]
        z = [point[2] for point in self.points_cloud]

        ax.plot(x,y,z)
        plt.show()

    def generate_solid(self):
        """Generate a solid object from the point cloud."""
        cloud = pv.PolyData(np.array(self.points_cloud))
        surf = cloud.delaunay_3d()
        voxels = pv.voxelize(surf, check_surface=False)
        coordinates = np.array(voxels.points)
        self.coordinates = np.array([[x, y, z] for x,y,z in coordinates])

    def save_coordinates(self, filename='data/coordinates.npy'):
        """Save the coordinates to a file."""
        np.save(filename, self.coordinates)
        np.save('data/center.npy', [self.cx, self.cy])

    def load_coordinates(self, filename='data/coordinates.npy'):
        """Load the coordinates from a file."""
        self.coordinates = np.load(filename)

    def plot_shell(self, plot_type="Surface"):
        """Plot the 3D surface or voxels."""
        cloud = pv.PolyData(np.array(self.points_cloud))
        surf = cloud.delaunay_3d()

        if plot_type == "Surface":
            surf.plot(show_edges=False)
        else:
            voxels = pv.voxelize(surf, check_surface=False)
            voxels.plot()

if __name__ == "__main__":
    
    img_index = [i for i in range(180)]
    image_folder = "images/reconstruction"
    images = [f'{image_folder}/angle_{i}.jpg' for i in img_index]

    processor = ImageProcessor(None)  # Initialize ImageProcessor with None image

    # Find contours for each image and get the contour with maximum area
    contours = [processor.find_tumour(image)[1] for image in images]

    s23 = SilhouetteTo3D() 

    for i,contour in enumerate(contours):
        s23.add_silhouette(contour, i)
    
    s23.convert_coordinates()

    s23.plot_shell()
    s23.generate_solid()
    s23.save_coordinates()


