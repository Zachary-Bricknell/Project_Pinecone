import numpy as np
import open3d as o3d
import os

def read_point_cloud(path):
    try:
        file_extension = path.split('.')[-1].lower()
        if file_extension in ['xyz', 'ply', 'las', 'laz']:
            # For '.laz' files, convert to '.las' first
            if file_extension == 'laz':
                laz_file = laspy.read(path)
                points = np.vstack((laz_file.x, laz_file.y, laz_file.z)).transpose()
                point_cloud = o3d.geometry.PointCloud()
                point_cloud.points = o3d.utility.Vector3dVector(points)
            else:
                # Directly read other supported file types
                point_cloud = o3d.io.read_point_cloud(path)

            # Extract only XYZ coordinates
            xyz_only = np.asarray(point_cloud.points)
            
            # Create a new point cloud with only XYZ
            new_point_cloud = o3d.geometry.PointCloud()
            new_point_cloud.points = o3d.utility.Vector3dVector(xyz_only)

            # Save the new point cloud as a PLY file
            new_file_path = os.path.splitext(path)[0] + ".ply"
            o3d.io.write_point_cloud(new_file_path, new_point_cloud)

            return new_point_cloud, new_file_path
        else:
            print(f"Unsupported file format: {file_extension}")
            return None, None
    except Exception as e:
        print(f"Error reading and converting the point cloud: {e}")
        return None, None
