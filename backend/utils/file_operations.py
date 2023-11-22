import bson
import gzip
import laspy
import numpy as np
import open3d as o3d

# Read the original pointcloud and ensure its a supported extension. Return a open3d object. 
def read_point_cloud(path):    
    try:        
        file_extension = path.split('.')[-1].lower()
        
        if file_extension in ['ply', 'las', 'pcd', 'xyz']:
            pcd = o3d.io.read_point_cloud(path)
        
        # Laz is compressed las and requires an additional step
        elif file_extension == 'laz':
            laz_file = laspy.read(path)
            points = np.vstack((laz_file.x, laz_file.y, laz_file.z)).transpose()
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(points)
            
        else:
            # Prompt for unsupported filetype
            # Current filetypes: Open3d compatible, laz, las, xyz
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Check if the point cloud is empty and raise an error
        if pcd.is_empty():
            raise ValueError("The point cloud has no points.")
        
        return pcd
    
    except Exception as e:
        print(f"Error reading the point cloud: {e}")
        return None

