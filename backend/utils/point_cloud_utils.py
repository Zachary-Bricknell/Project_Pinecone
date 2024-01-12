import os
import open3d as o3d
import numpy as np
from utils.file_operations import modify_filename
from utils.point_cloud_clean_data import clean_point_cloud_data
from utils.point_cloud_preprocess import preprocess_point_cloud

def process_point_cloud(filepath):
    new_filepath, step_complete = clean_point_cloud_data(filepath)
    
    if not step_complete:
        print(f"Data is cleaned.")
        return
    
    #template and not functional yet
    new_filepath, step_complete = preprocess_point_cloud();
    
    ## Step 2

    ## Step 3
    
    

def save_processed_file(directory, filename, point_cloud):
    """
    Parameters:
    directory (str): The base directory to save the file in.
    filename (str): The name of the file to save.
    point_cloud (open3d.geometry.PointCloud): The point cloud to save.

    Returns:
    str: The path to the saved file.
    
    Description:
    Saves the processed point cloud file in a designated 'processed' folder within the specified directory.
    """
    processed_directory = os.path.join(directory, "processed")
    if not os.path.exists(processed_directory):
        os.makedirs(processed_directory)

    processed_file_path = os.path.join(processed_directory, f'pineconed_{filename}.ply')
    o3d.io.write_point_cloud(processed_file_path, point_cloud)
    return processed_file_path

def visualize_point_cloud(path):
    """
    Parameters:
    path (str): The file path of the point cloud to visualize.

    Returns: 
    none
    
    Description:
    Opens and visualizes a point cloud from a given file path.
    """
    # Adjust the path to remove the .pp suffix to be able to open regardless of what stage of preprocessing it is on. 
    base_name, ext = os.path.splitext(path)
    if ext.startswith('.pp'):
        # Extract the original extension
        original_ext = os.path.splitext(base_name)[1]
        adjusted_path = base_name + original_ext
    else:
        adjusted_path = path

    point_cloud = o3d.io.read_point_cloud(adjusted_path)
    if point_cloud is None:
        raise ValueError("Could not read point cloud for visualization.")

    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(point_cloud)
    vis.run()
    vis.destroy_window()