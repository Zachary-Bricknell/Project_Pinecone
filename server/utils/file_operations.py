import bson
import gzip
import laspy
import numpy as np
import open3d as o3d

# Serialize the Point Cloud file without compressing to "save state" as needed
def serialize_pc(data_dict):
    return bson.BSON.encode(data_dict)

# Compress the file
def compress_bson(bson_data, output_path):
    with gzip.open(output_path, "wb") as pc:
        pc.write(bson_data)

# Decompress and Deseialize as both operations are generall performed together to read
def decompress_bson(file_path):
    with gzip.open(file_path, 'rb') as file:
        bson_data = file.read()
    data_dict = bson.loads(bson_data)
    
    # Extract points and convert them to a numpy array
    points_array = np.asarray(data_dict['points'])
    
    # Create a new point cloud with the extracted points
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(points_array)

    return point_cloud

# Read the original pointcloud and ensure its a supported extension. Return a open3d object. 
def read_point_cloud(path):
    try:
        file_extension = path.split('.')[-1].lower()
        if file_extension in ['ply', 'las']:
            pcd = o3d.io.read_point_cloud(path)
        elif file_extension == 'laz':
            laz_file = laspy.read(path)
            points = np.vstack((laz_file.x, laz_file.y, laz_file.z)).transpose()
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(points)
        else:
            # Prompt for unsupported filetype
            # Current filetypes: Open3d compatible, laz, las
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Check if the point cloud is empty and raise an error
        if pcd.is_empty():
            raise ValueError("The point cloud has no points.")
        
        return pcd
    except Exception as e:
        print(f"Error reading the point cloud: {e}")
        return None

