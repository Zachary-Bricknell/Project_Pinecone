from tkinter import CURRENT
import open3d as o3d
import os
import numpy as np
import logging
from utils.file_operations import setup_logging, write_to_file
from utils.config import STAGE_PREFIXES

# Map of the order of functions for this stage with the value being the name of the function to be called
cleaning_operations = {
    0: 'extract_xyz_coordinates',
    1: 'remove_statistical_outliers',
    # 2: 'remove_radius_outliers',
    2: 'voxel_downsample',
}

def cleaning_stage(filepath, log_path):
    """
    Description:
    Driver code for the cleaning stage execution.

    Parameters:
    filepath (str): The file path of the input point cloud.
    current_step (int): The current step in the cleaning process.
    stage_prefix (str): The prefix of the current cleaning stage.
    log_path (str): The path to store log files.

    Returns:
    tuple: A tuple containing the (str)filepath of the cleaned point cloud and a (bool)flag indicating completion.
    """
    setup_logging("cleaning_stage", log_path)
    point_cloud = o3d.io.read_point_cloud(filepath)
    logging.info("Executing Cleaning Stage...")
    current_step = 0 
    
    while current_step in cleaning_operations:
        operation = cleaning_operations[current_step]
        
        try:
            # Retrieve the operation function by name and execute it.
            operation_function = globals()[operation]
            point_cloud, step_completed = operation_function(point_cloud)
            
            if not step_completed:
                logging.error(f"Step failed in {operation}, exiting...")
                return filepath, False
            
            current_step += 1

            if current_step == len(cleaning_operations): 
                new_filepath = write_to_file(point_cloud, filepath,"_cl")
                logging.info("Cleaning stage completed.")
                return new_filepath, True
            
        except Exception as e:
            logging.error(f"Error in {operation}: {e}")
            break  
        
    return new_filepath, False

def extract_xyz_coordinates(point_cloud):
    """
    Description:
    Extracts XYZ coordinates from a file, removing excess values such as RGB.

    Parameters:
    point_cloud (open3d.geometry.PointCloud): The point cloud to process.
    filepath (str): The file path of the point cloud.
    stage_prefix (str): The prefix of the current step.
    current_step (int): The current processing step.

    Returns:
    tuple: A tuple containing the new (open3d.geometry.PointCloud) point cloud, its corresponding (str)file path and the (bool) success flag.
    """
    logging.info("Extracting XYZ coordinates...")  
    try:
        xyz = np.asarray(point_cloud.points)
        new_point_cloud = o3d.geometry.PointCloud()
        new_point_cloud.points = o3d.utility.Vector3dVector(xyz)
        return new_point_cloud, True
    except Exception as e:
        logging.error(f"Failed to extract XYZ coordinates: {e}")
        return point_cloud, False

#@@ Deprecated but left in as an example @@#
def remove_radius_outliers(point_cloud, nb_neighbors=15, radius=0.05):
    """
    Description:
    Removes radius outliers from a point cloud and saves the intermediate state.

    Parameters:
    point_cloud (open3d.geometry.PointCloud): The point cloud to process.
    filepath (str): The file path of the point cloud.
    stage_prefix (str): The prefix of the current step.
    current_step (int): The current processing step.
    nb_neighbors (int): Number of neighbors to use for radius outlier removal. Default is 15.
    radius (float): Radius for outlier removal. Default is 0.05.

    Returns:
    str: Filepath of the point cloud after removing radius outliers.
    """
    logging.info("Attempting to remove radius outliers...")
    try:
        _, rad_ind = point_cloud.remove_radius_outlier(nb_points=nb_neighbors, radius=radius)
        new_point_cloud = point_cloud.select_by_index(rad_ind)
        logging.info("Radius outliers removed")
        return new_point_cloud, True
    except Exception as e:
        logging.error(f"Failed to remove Radius Outliers: {e}")
        return point_cloud, False

def remove_statistical_outliers(point_cloud, nb_neighbors = 20, std_ratio = 1.0):
    """
    Description:
    Removes statistical outliers from a point cloud and saves the intermediate state.

    Parameters:
    point_cloud (open3d.geometry.PointCloud): The point cloud to process.
    filepath (str): The file path of the point cloud.
    stage_prefix (str): The prefix of the current step.
    current_step (int): The current processing step.
    nb_neighbors (int): Number of neighbors to use for statistical outlier removal. Default is 20.
    std_ratio (float): Standard deviation ratio for statistical outlier removal. Default is 1.0.

    Returns:
    tuple: A tuple containing the new (open3d.geometry.PointCloud) point cloud, its corresponding (str)file path and the (bool) success flag.
    """
    logging.info("Removing statistical outliers...")   
    try:
        cl, ind = point_cloud.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
        new_point_cloud = point_cloud.select_by_index(ind)
        return new_point_cloud, True
    except Exception as e:
        logging.error(f"Failed to remove statistical outliers: {e}")
        return point_cloud, False

def voxel_downsample(point_cloud, voxel_size = 0.02):
    """
    Description:
    Downsamples a point cloud using the voxel grid downsampling.

    Parameters:
    point_cloud (open3d.geometry.PointCloud): The point cloud to process.
    filepath (str): The file path of the point cloud.
    stage_prefix (str): The prefix of the current step.
    current_step (int): The current processing step.
    voxel_size (float): Voxel size for downsampling. Default is 0.02.

    Returns:
    tuple: A tuple containing the new (open3d.geometry.PointCloud) point cloud, its corresponding (str)file path and the (bool) success flag.
    """
    logging.info("Voxel downsampling...")    
    try:
        new_point_cloud = point_cloud.voxel_down_sample(voxel_size=voxel_size)
        return new_point_cloud, True
    except Exception as e:
        logging.error(f"Failed to voxel downsample: {e}")
        return point_cloud, False