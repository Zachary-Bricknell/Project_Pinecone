import os
import open3d as o3d
import numpy as np
from utils.file_operations import modify_filename


def get_current_preprocessing_step(filepath):
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
    
    # Check if filename contains preprocessing step pattern (e.g., "_pp1")
    if '_pp' in name:
        try:
            # Extract and return the numerical part of the preprocessing step
            return int(name.split('_pp')[-1])
        except ValueError:
            # If extraction fails, return 0 indicating no preprocessing step
            pass
    
    return 0

def process_point_cloud(filepath, statistical_nb_neighbors=20, std_ratio=1.0, radius_nb_neighborus=15, radius=0.05, voxel_size=0.02):
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
    
    Description:
    Processes a given point cloud by removing outliers and applying voxel downsampling. 
    Iterates depending on the current step, obtained from get_current_preprocessing_step(path);
    """    

    current_step = get_current_preprocessing_step(filepath)
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
    
    return filepath

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

    new_filepath = modify_filename(filepath, "1")  # Preprocessing step 1
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
        print(f"Inside remove_statistical_outliers - Types: {type(point_cloud)}, {type(filepath)}, {type(nb_neighbors)}, {type(std_ratio)}")
        print(f"Inside remove_statistical_outliers - Values: {point_cloud}, {filepath}, {nb_neighbors}, {std_ratio}")
        print("Removing Statistical Outliers.")
        cl, ind = point_cloud.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
        # Use the inlier index to select the points
        point_cloud = point_cloud.select_by_index(ind)
        new_filepath = modify_filename(filepath, "2")  # Preprocessing step 2
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
        new_filepath = modify_filename(filepath, "3")  # Preprocessing step 3
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
        new_filepath = modify_filename(filepath, "4")  # Preprocessing step 4
        o3d.io.write_point_cloud(new_filepath, point_cloud)
        return new_filepath
    except Exception as e:
        print(f"Failed to Voxel Downsample: {e}")
        return filepath

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