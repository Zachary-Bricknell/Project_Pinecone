import numpy as np
import open3d as o3d
import os
import laspy

def read_point_cloud(path):
    try:
        file_extension = path.split('.')[-1].lower()
        filename_without_extension = os.path.splitext(os.path.basename(path))[0]

        # Check if the file already ends with "_xyz.ply" 
        if filename_without_extension.endswith('_xyz') and file_extension == 'ply':
            print("File is already an XYZ-only PLY file.")
            return o3d.io.read_point_cloud(path), path

        if file_extension in ['xyz', 'ply', 'las', 'laz']:
            # For '.laz' files, convert to '.las' first
            if file_extension == 'laz':
                laz_file = laspy.read(path)
                points = np.vstack((laz_file.x, laz_file.y, laz_file.z)).transpose()
                point_cloud = o3d.geometry.PointCloud()
                point_cloud.points = o3d.utility.Vector3dVector(points)
            else:
                # Other filetipes don't require additional processing
                point_cloud = o3d.io.read_point_cloud(path)

            # Extract only XYZ coordinates removing RGB and Normals if present
            xyz_only = np.asarray(point_cloud.points)
            
            # Create a new point cloud with only XYZ
            new_point_cloud = o3d.geometry.PointCloud()
            new_point_cloud.points = o3d.utility.Vector3dVector(xyz_only)

            # Save the new point cloud as a PLY file with _xyz denoting that we have extracted only XYZ points
            new_file_path = os.path.splitext(path)[0] + "_xyz.ply"
            o3d.io.write_point_cloud(new_file_path, new_point_cloud)

            return new_point_cloud, new_file_path
        else:
            print(f"Unsupported file format: {file_extension}")
            return None, None
    except Exception as e:
        print(f"Error reading and converting the point cloud: {e}")
        return None, None
