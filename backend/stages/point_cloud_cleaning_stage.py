from sre_constants import SUCCESS
import open3d as o3d
import os
import numpy as np
import logging
from utils.file_operations import modify_filename, setup_logging
from utils.point_cloud_utils import get_current_step
from utils.config import STAGE_PREFIXES

# Map of the order of functions for this stage with the value being the name of the function to be called
cleaning_operations = {
    0: 'extract_xyz_coordinates',
    1: 'remove_statistical_outliers',
    # 2: 'remove_radius_outliers',
    2: 'voxel_downsample',
}

def cleaning_stage(filepath, current_step, stage_prefix, log_path):
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
    done_cleaning_data = False
    step_completed = False

    logging.info("Executing Cleaning Stage...")
    while current_step in cleaning_operations:
        operation = cleaning_operations[current_step]
        try:
            # Uses the step number and function name from 'cleaning_operations' to execute the functions in order.
            point_cloud, filepath, step_completed = globals()[operation](point_cloud, filepath, stage_prefix, current_step)
            if not step_completed:
                logging.error("Step failed, exiting...")
                return
            current_step += 1            
            if current_step == len(cleaning_operations): 
                done_cleaning_data = True
                filepath = modify_filename(filepath, "_pp", "0")
                o3d.io.write_point_cloud(filepath, point_cloud)
        except Exception as e:
            logging.error(f"Error in {operation}: {e}")
            break 

    logging.info("Cleaning stage completed.")
    return filepath, done_cleaning_data

def extract_xyz_coordinates(point_cloud, filepath, stage_prefix, current_step):
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
    success_flag = False    
    try:
        xyz = np.asarray(point_cloud.points)
        new_point_cloud = o3d.geometry.PointCloud()
        new_point_cloud.points = o3d.utility.Vector3dVector(xyz)
        filepath = modify_filename(filepath, stage_prefix, current_step)
        success_flag = True
    except Exception as e:
        logging.error(f"Failed to extract XYZ coordinates: {e}")

    return new_point_cloud, filepath, success_flag

def remove_radius_outliers(point_cloud, filepath, stage_prefix, current_step, nb_neighbors=15, radius=0.05):
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
        point_cloud = point_cloud.select_by_index(rad_ind)
        filepath = modify_filename(filepath, stage_prefix, current_step)  # Updated to use current_step
        o3d.io.write_point_cloud(filepath, point_cloud)
        logging.info("Radius outliers removed")
        return filepath
    
    except Exception as e:
        logging.error(f"Failed to remove Radius Outliers: {e}")
        return filepath

def remove_statistical_outliers(point_cloud, filepath, stage_prefix, current_step, nb_neighbors = 20, std_ratio = 1.0):
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
    success_flag = False    
    try:
        cl, ind = point_cloud.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
        point_cloud = point_cloud.select_by_index(ind)
        filepath = modify_filename(filepath, stage_prefix, current_step)
        success_flag = True
    except Exception as e:
        logging.error(f"Failed to remove statistical outliers: {e}")
    return point_cloud, filepath, success_flag

def voxel_downsample(point_cloud, filepath, stage_prefix, current_step, voxel_size = 0.02):
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
    success_flag = False    
    try:
        point_cloud = point_cloud.voxel_down_sample(voxel_size=voxel_size)
        filepath = modify_filename(filepath, stage_prefix, current_step)
        success_flag = True
    except Exception as e:
        logging.error(f"Failed to voxel downsample: {e}")
    return point_cloud, filepath, success_flag