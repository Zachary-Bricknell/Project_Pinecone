import numpy as np
import open3d as o3d
import laspy

def read_point_cloud(path):
    try:
        file_extension = path.split('.')[-1].lower()

        # Load the point cloud file depending on the file extension
        if file_extension in ['ply', 'las', 'laz', 'xyz']:
            # For .laz files, use laspy to read the compressed .las file
            if file_extension == 'laz':
                laz_file = laspy.read(path)
                points = np.vstack((laz_file.x, laz_file.y, laz_file.z)).transpose()
            else:
                # For other file types, use numpy.loadtxt to read only the first three columns
                points = np.loadtxt(path, usecols=(0, 1, 2))

            # Create an Open3D point cloud object with the XYZ data
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(points)
            return pcd

        else:
            # Unsupported file format
            raise ValueError(f"Unsupported file format: {file_extension}")

    except Exception as e:
        print(f"Error reading the point cloud: {e}")
        return None
