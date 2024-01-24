import scipy.io
import numpy as np
import cv2
import glob
import vtk
from teste import find_tumour

class VoxelReconstructor:
    def __init__(self, data_path, camera_matrix, image_format='.ppm', voxel_size=120):
        self.data_path = data_path
        self.camera_matrix = camera_matrix
        self.image_format = image_format
        self.voxel_size = voxel_size

        self.images = None
        self.silhouette = None
        self.voxel_grid = None
        self.occupancy = None

    def load_images(self):
        files = sorted(glob.glob(f"{self.data_path}/angle_*.jpg"))
        self.images = []
        for f in files:
            im = cv2.imread(f, cv2.IMREAD_UNCHANGED).astype(float) / 255
            self.images.append(im[:, :, ::-1])

    def extract_silhouette(self):
        image_folder = "images/reconstruction"

        self.silhouettes = [f'{image_folder}/angle_{i}.jpg' for i in range(360)]
        self.silhouettes = [find_tumour(image)[0] for image in silhouettes]
        
    def create_voxel_grid(self):
        s = self.voxel_size
        x, y, z = np.mgrid[:s, :s, :s]
        pts = np.vstack((x.flatten(), y.flatten(), z.flatten())).astype(float)
        pts = pts.T
        xmax, ymax, zmax = np.max(pts, axis=0)
        pts[:, 0] /= xmax
        pts[:, 1] /= ymax
        pts[:, 2] /= zmax
        center = pts.mean(axis=0)
        pts -= center
        pts /= 5
        pts[:, 2] -= 0.62

        self.voxel_grid = np.vstack((pts.T, np.ones((1, pts.shape[0]))))

    def generate_object_transformations(self, num_images=360):
        transformations = []
        angle_deg_increment = 360 / num_images
        for i in range(num_images):
            angle_rad = np.radians(i * angle_deg_increment)
            R = np.array([
                [np.cos(angle_rad), 0, np.sin(angle_rad)],
                [0, 1, 0],
                [-np.sin(angle_rad), 0, np.cos(angle_rad)]
            ])
            transformations.append(R)
        return transformations

    def calculate_occupancy(self):
        imgH, imgW, __ = self.images[0].shape
        object_transformations = self.generate_object_transformations(len(self.images))

        filled = []
        for R_obj, im in zip(object_transformations, self.silhouette):
            transformed_pts = R_obj @ self.voxel_grid[:3, :]
            pts_homogeneous = np.vstack((transformed_pts, np.ones((1, transformed_pts.shape[1]))))

            uvs = self.camera_matrix @ pts_homogeneous
            uvs /= uvs[2, :]
            uvs = np.round(uvs).astype(int)

            x_good = np.logical_and(uvs[0, :] >= 0, uvs[0, :] < imgW)
            y_good = np.logical_and(uvs[1, :] >= 0, uvs[1, :] < imgH)
            good = np.logical_and(x_good, y_good)
            indices = np.where(good)[0]
            fill = np.zeros(uvs.shape[1])
            sub_uvs = uvs[:2, indices]
            res = im[sub_uvs[1, :], sub_uvs[0, :]]
            fill[indices] = res 

            filled.append(fill)

        self.filled = np.vstack(filled)
        self.occupancy = np.sum(self.filled, axis=0)

    def save_point_cloud(self, filename="shape.txt"):
        with open(filename, "w") as fout:
            fout.write("x,y,z,occ\n")
            for occ, p in zip(self.occupancy, self.voxel_grid[:, :3]):
                fout.write(",".join(p.astype(str)) + "," + str(occ) + "\n")

    def save_as_rectilinear_grid(self, filename="shape.vtr"):
        xCoords = vtk.vtkFloatArray()
        yCoords = vtk.vtkFloatArray()
        zCoords = vtk.vtkFloatArray()
        values = vtk.vtkFloatArray()

        for i in range(self.voxel_size):
            xCoords.InsertNextValue(self.voxel_grid[i, 0])
            yCoords.InsertNextValue(self.voxel_grid[i, 1])
            zCoords.InsertNextValue(self.voxel_grid[i, 2])
            values.InsertNextValue(self.occupancy[i])

        rgrid = vtk.vtkRectilinearGrid()
        rgrid.SetDimensions(self.voxel_size, self.voxel_size, self.voxel_size)
        rgrid.SetXCoordinates(xCoords)
        rgrid.SetYCoordinates(yCoords)
        rgrid.SetZCoordinates(zCoords)
        rgrid.GetPointData().SetScalars(values)

        writer = vtk.vtkXMLRectilinearGridWriter()
        writer.SetFileName(filename)
        writer.SetInputData(rgrid)
        writer.Write()

    def run(self):
        self.load_images()
        self.extract_silhouette()
        self.create_voxel_grid()
        self.calculate_occupancy()
        self.save_point_cloud()
        self.save_as_rectilinear_grid()

if __name__ == "__main__":
    # Usage example
    camera_matrix = load_calibration_data()[0]
    reconstructor = VoxelReconstructor(data_path="data", camera_matrix=camera_matrix)
    reconstructor.run()

