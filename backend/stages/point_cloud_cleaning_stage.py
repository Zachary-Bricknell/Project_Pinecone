import open3d as o3d
import os
import numpy as np
import logging
from utils.file_operations import modify_filename, setup_logging
from utils.point_cloud_utils import get_current_step
from utils.config import STAGE_PREFIXES

def cleaning_stage(filepath, current_step, stage_prefix, log_path, statistical_nb_neighbors=20, std_ratio=1.0, radius_nb_neighbors=15, radius=0.05, voxel_size=0.02):
    """
    Parameters:
    filepath (str): The file path of the point cloud to process.
    current_step (int): The current step in the cleaning process.
    stage_prefix (str): The prefix of the current step. 
    statistical_nb_neighbors (int): Number of neighbors to use for statistical outlier removal.
    std_ratio (float): Standard deviation ratio for statistical outlier removal.
    radius_nb_neighbors (int): Number of neighbors to use for radius-based outlier removal.
    radius (float): Radius value for radius-based outlier removal.
    voxel_size (float): Size of the voxel for downsampling.

    Returns:
    str: Filepath of the processed point cloud after the current step.
    bool: True if all cleaning steps are complete, False otherwise.

    description:
    Cleans the point cloud data based on the current cleaning step. Each step is done in order. once last step is done,
    trigger the bool flag to return true. 
    """
    setup_logging("cleaning_stage", log_path)    
    point_cloud = o3d.io.read_point_cloud(filepath)
    done_cleaning_data = False
    logging.info("Executing Cleaning Stage...")
    if current_step == 0:
        filepath = extract_xyz_coordinates(point_cloud, filepath, stage_prefix)
        current_step = 1
        filepath = modify_filename(filepath, stage_prefix, current_step)

    if current_step == 1:
        filepath = remove_statistical_outliers(point_cloud, filepath, stage_prefix, statistical_nb_neighbors, std_ratio)
        current_step = 2
        filepath = modify_filename(filepath, stage_prefix, current_step)

    if current_step == 2:
        # Currently unavailable until further testing.
        # filepath = remove_radius_outliers(point_cloud, filepath, stage_prefix, radius_nb_neighbors, radius)
        current_step = 3
        filepath = modify_filename(filepath, stage_prefix, current_step)

    if current_step == 3:
        filepath = voxel_downsample(point_cloud, filepath, stage_prefix, voxel_size)
        done_cleaning_data = True

    logging.info("Cleaning stage completed...")
    return filepath, done_cleaning_data

def extract_xyz_coordinates(point_cloud, filepath, current_stage_prefix):
    """
    Parameters:
    point_cloud (open3d.geometry.PointCloud): The point cloud from which to extract XYZ coordinates.
    filepath (str): The file path of the point cloud.
    current_stage_prefix (str): The prefix of the current step. 
    
    Returns:
    str: Filepath of the point cloud after extracting only XYZ coordinates.
    
    Description:
    Extracts only the XYZ coordinates from a point cloud, discarding any additional information, notably any RGB data. 
    It saves the point cloud and saves the intermediate state.
    """
    logging.info("Attempting to extract XYZ coordinates...")
    try:        
        xyz = np.asarray(point_cloud.points)
        new_point_cloud = o3d.geometry.PointCloud()
        new_point_cloud.points = o3d.utility.Vector3dVector(xyz)

        new_filepath = modify_filename(filepath, current_stage_prefix, "1")  # cleaning step 1
        logging.info("xyz coordinates have been extracted")
        o3d.io.write_point_cloud(new_filepath, new_point_cloud)
        
        return new_filepath
    
    except Exception as e:
        logging.error(f"Failed to extract xyz coordinates: {e}")
        return filepath

def remove_statistical_outliers(point_cloud, filepath, current_stage_prefix, nb_neighbors, std_ratio):
    """
    Parameters:
    point_cloud (open3d Object): The point cloud to process.
    filepath (str): The file path of the point cloud.
    current_stage_prefix (str): The prefix of the current step. 
    nb_neighbors (int): Number of neighbors to use for outlier removal.
    std_ratio (float): Standard deviation ratio.

    Returns:
    str: Filepath of the point cloud after removing statistical outliers.
    
    Description:
    Removes statistical outliers from a point cloud and saves the intermediate state.
    """
    logging.info("Attempting to remove statistical outliers...")
    try:
        cl, ind = point_cloud.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
        # Use the inlier index to select the points
        point_cloud = point_cloud.select_by_index(ind)
        new_filepath = modify_filename(filepath, current_stage_prefix, "2")  # cleaning 2
        o3d.io.write_point_cloud(new_filepath, point_cloud)
        logging.info(f"Statistical outliers Removed.")

        return new_filepath
    
    except Exception as e:
        logging.error(f"Failed to remove Statistical Outliers: {e}")
        return filepath

def remove_radius_outliers(point_cloud, filepath, current_stage_prefix, nb_neighbors, radius):
    """
    Parameters:
    point_cloud (open3d.geometry.PointCloud): The point cloud to process.
    filepath (str): The file path of the point cloud.
    current_stage_prefix (str): The prefix of the current step. 
    nb_neighbors (int): Number of neighbors to use for radius outlier removal.
    radius (float): Radius for outlier removal.

    Returns:
    str: Filepath of the point cloud after removing radius outliers.
    
    Description:
    Removes radius outliers from a point cloud and saves the intermediate state.
    """
    logging.info("Attempting to remove radius outliers...")
    try:
        _, rad_ind = point_cloud.remove_radius_outlier(nb_points=nb_neighbors, radius=radius)
        point_cloud = point_cloud.select_by_index(rad_ind)
        new_filepath = modify_filename(filepath, current_stage_prefix, "3")  # cleaning step 3
        o3d.io.write_point_cloud(new_filepath, point_cloud)
        logging.info("Radius outliers removed")
        return new_filepath
    
    except Exception as e:
        logging.error(f"Failed to remove Radius Outliers: {e}")
        return filepath

def voxel_downsample(point_cloud, filepath, current_stage_prefix, voxel_size):
    """
    Parameters:
    point_cloud (open3d.geometry.PointCloud): The point cloud to downsample.
    filepath (str): The file path of the point cloud.
    current_stage_prefix (str): The prefix of the current step. 
    voxel_size (float): Size of the voxel for downsampling.

    Returns:
    str: Filepath of the downsampled point cloud.
    
    Description:
    Applies voxel downsampling to a point cloud and saves.
    """
    logging.info("Attempting to voxel downsample...")
    try:
        point_cloud = point_cloud.voxel_down_sample(voxel_size=voxel_size)
        new_filepath = modify_filename(filepath, "_pp", "0")  # cleaning step 4
        o3d.io.write_point_cloud(new_filepath, point_cloud)
        logging.info("Voxel Downsampled the point cloud.")
        return new_filepath
    
    except Exception as e:
        logging.error(f"Failed to Voxel Downsample: {e}")
        return filepath