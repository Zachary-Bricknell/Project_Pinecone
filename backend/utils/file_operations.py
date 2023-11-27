import numpy as np
import open3d as o3d
import os
import laspy

# Attempts to read the pointcloud extensions and remove any points beyond x y z. Returns a o3d object. 
def read_point_cloud(path):
    try:
        file_extension = path.split('.')[-1].lower()
        filename_without_extension = os.path.splitext(os.path.basename(path))[0]

        if filename_without_extension.endswith('_xyz') and file_extension == 'ply':
            print("File is already an XYZ-only PLY file.")
            return o3d.io.read_point_cloud(path)

        if file_extension in ['xyz', 'ply', 'las', 'laz']:
            if file_extension == 'laz':
                laz_file = laspy.read(path)
                points = np.vstack((laz_file.x, laz_file.y, laz_file.z)).transpose()
                point_cloud = o3d.geometry.PointCloud()
                point_cloud.points = o3d.utility.Vector3dVector(points)
            else:
                point_cloud = o3d.io.read_point_cloud(path)
            return point_cloud

        else:
            print(f"Unsupported file format: {file_extension}")
            return None

    except Exception as e:
        print(f"Error reading and converting the point cloud: {e}")
        return None
