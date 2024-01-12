import open3d as o3d
import os
import numpy as np
from utils.file_operations import modify_filename

#Global variable to denote the naming for the data cleaning stage
data_cleaning_identifier = "_cl"

def get_current_cleaning_step(filepath):
    """
    Parameters:
    filepath (str): The file path of the point cloud.

    Returns:
    int: The current preprocessing step (0 if none).
    
    Description:
    Extracts the preprocessing step from the filename, denoted with ppX where X is the step number last completed.
    """
    filename = os.path.basename(filepath)
    name, _ = os.path.splitext(filename)
    
    # Check if filename contains cleaning step pattern (e.g., "_cl1")
    if data_cleaning_identifier in name:
        try:
            # Extract and return the numerical part of the preprocessing step
            return int(name.split(data_cleaning_identifier)[-1])
        except ValueError:
            # If extraction fails, return 0 indicating no preprocessing step
            pass
    
    return 0

def clean_point_cloud_data(filepath, statistical_nb_neighbors=20, std_ratio=1.0, radius_nb_neighborus=15, radius=0.05, voxel_size=0.02):
    """
    Parameters:
    filepath (str): The file path of the point cloud to process.
    statistical_nb_neighbors (int): Number of neighbors to use for outlier removal.
    std_ratio (float): Standard deviation ratio.
    radius_nb_neighbors (int): Number of neighbors to use for outlier removal.
    std_ratio (float): Standard deviation ratio.
    voxel_size (float): Size of the voxel for downsampling.

    Returns:
    str: Filepath of the final processed point cloud.
    bool: True or False if the point cloud has gone throguh all data cleaning steps
    
    Description:
    Cleans a given point cloud by removing outliers and applying voxel downsampling. 
    Iterates depending on the current step, once all steps are done sets the flag to true
    """    
    # Set to true when all steps have been checked and the data is cleaned
    done_cleaning_data = False
    current_step = get_current_cleaning_step(filepath)
    point_cloud = o3d.io.read_point_cloud(filepath)

    if current_step < 1:
        print("Extracting XYZ coordinates.")
        filepath = extract_xyz_coordinates(point_cloud, filepath)
        current_step = 1
       
    if current_step < 2:
        filepath = remove_statistical_outliers(point_cloud, filepath, statistical_nb_neighbors, std_ratio)
        current_step = 2 
    
    # Requires further testing to identify the bottleneck.
    # if current_step < 3:
    #     filepath = remove_radius_outliers(point_cloud, filepath, radius_nb_neighbors, radius)
    #     current_step = 3 

    if current_step < 4:
        filepath = voxel_downsample(point_cloud, filepath, voxel_size)
        done_cleaning_data = True 

    return filepath, done_cleaning_data

def extract_xyz_coordinates(point_cloud, filepath):
    """
    Parameters:
    point_cloud (open3d.geometry.PointCloud): The point cloud from which to extract XYZ coordinates.
    filepath (str): The file path of the point cloud.

    Returns:
    str: Filepath of the point cloud after extracting only XYZ coordinates.
    
    Description:
    Extracts only the XYZ coordinates from a point cloud, discarding any additional information, notably any RGB data. 
    It saves the point cloud and saves the intermediate state.
    """
    xyz = np.asarray(point_cloud.points)
    new_point_cloud = o3d.geometry.PointCloud()
    new_point_cloud.points = o3d.utility.Vector3dVector(xyz)

    new_filepath = modify_filename(filepath, data_cleaning_identifier, "1")  # cleaning step 1
    o3d.io.write_point_cloud(new_filepath, new_point_cloud)

    return new_filepath


def remove_statistical_outliers(point_cloud, filepath, nb_neighbors, std_ratio):
    """
    Parameters:
    point_cloud (open3d Object): The point cloud to process.
    filepath (str): The file path of the point cloud.
    nb_neighbors (int): Number of neighbors to use for outlier removal.
    std_ratio (float): Standard deviation ratio.

    Returns:
    str: Filepath of the point cloud after removing statistical outliers.
    
    Description:
    Removes statistical outliers from a point cloud and saves the intermediate state.
    """
    try:
        cl, ind = point_cloud.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
        # Use the inlier index to select the points
        point_cloud = point_cloud.select_by_index(ind)
        new_filepath = modify_filename(filepath, data_cleaning_identifier, "2")  # cleaning 2
        o3d.io.write_point_cloud(new_filepath, point_cloud)
        print(f"PointCloud after statistical outlier removal has {len(point_cloud.points)} points.")

        return new_filepath
    except Exception as e:
        print(f"Failed to remove Statistical Outliers: {e}")
        return filepath

def remove_radius_outliers(point_cloud, filepath, nb_neighbors, radius):
    """
    Parameters:
    point_cloud (open3d.geometry.PointCloud): The point cloud to process.
    filepath (str): The file path of the point cloud.
    nb_neighbors (int): Number of neighbors to use for radius outlier removal.
    radius (float): Radius for outlier removal.

    Returns:
    str: Filepath of the point cloud after removing radius outliers.
    
    Description:
    Removes radius outliers from a point cloud and saves the intermediate state.
    """
    try:
        print("Removing Radius Outliers.")
        _, rad_ind = point_cloud.remove_radius_outlier(nb_points=nb_neighbors, radius=radius)
        point_cloud = point_cloud.select_by_index(rad_ind)
        new_filepath = modify_filename(filepath, data_cleaning_identifier, "3")  # cleaning step 3
        o3d.io.write_point_cloud(new_filepath, point_cloud)
        return new_filepath
    except Exception as e:
        print(f"Failed to remove Radius Outliers: {e}")
        return filepath

def voxel_downsample(point_cloud, filepath, voxel_size):
    """
    Parameters:
    point_cloud (open3d.geometry.PointCloud): The point cloud to downsample.
    filepath (str): The file path of the point cloud.
    voxel_size (float): Size of the voxel for downsampling.

    Returns:
    str: Filepath of the downsampled point cloud.
    
    Description:
    Applies voxel downsampling to a point cloud and saves.
    """
    try:
        print("Voxel Downsampling.")
        point_cloud = point_cloud.voxel_down_sample(voxel_size=voxel_size)
        new_filepath = modify_filename(filepath, data_cleaning_identifier, "4")  # cleaning step 4
        o3d.io.write_point_cloud(new_filepath, point_cloud)
        return new_filepath
    except Exception as e:
        print(f"Failed to Voxel Downsample: {e}")
        return filepath