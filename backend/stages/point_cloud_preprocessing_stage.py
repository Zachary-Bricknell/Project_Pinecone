import os
import open3d as o3d
import numpy as np
import time
import logging
from utils.file_operations import modify_filename, setup_logging
from sklearn.ensemble import IsolationForest

# Map of the order of functions for this stage with the value being the name of the function to be called
# Parameters can be updated here which will be passed into the function
preprocessing_operations = {
    0: {'function': 'ground_segmentation', 'params': {}},
    1: {'function': 'remove_outliers_isolation_forest', 'params': {'num_iterations': 12}},
    2: {'function': 'keep_only_largest_cluster', 'params': {}},
}

def preprocessing_stage(filepath, current_step, stage_prefix, log_path):
    """
    Parameters:
    filepath (str): The file path of the input point cloud.
    current_step (int): The current step in the preprocessing process.
    stage_prefix (str): The prefix of the current preprocessing stage.
    log_path (str): The path to store log files.

    Returns:
    str: The file path of the final processed point cloud.
    bool: True if the preprocessing is successful, False otherwise.
    
    Description:
    This function preprocesses a point cloud by dynamically executing the defined operations.
    """
    
    setup_logging("preprocessing_stage", log_path)
    logging.info("Preprocessing Stage Initiated")
    point_cloud = o3d.io.read_point_cloud(filepath)
    done_preprocessing = False
    new_filepath = filepath

    while current_step in preprocessing_operations and not done_preprocessing:
        operation_info = preprocessing_operations[current_step]
        operation_function = globals()[operation_info['function']]
        operation_params = operation_info['params']

        try:
            if operation_params:
                point_cloud, success_flag = operation_function(point_cloud, **operation_params)
            else:
                point_cloud, success_flag = operation_function(point_cloud)
                
            if not success_flag:
                logging.error(f"Error in {operation_info['function']}, exiting...")
                return None, False
                
            current_step += 1
            if current_step == len(preprocessing_operations):
                done_preprocessing = True 
            
        except Exception as e:
            logging.error(f"Error in {operation_info['function']}: {e}")
            return None, False

    if done_preprocessing:
        new_filepath = modify_filename(new_filepath, '_PC' , 0)
        o3d.io.write_point_cloud(new_filepath, point_cloud)
        logging.info("Preprocessing Stage Completed successfully.")
        return new_filepath, True
    else:
        return None, False

def ground_segmentation(point_cloud):
    """
    Parameters:
    point_cloud (open3d.geometry.PointCloud): The point cloud to process.

    Returns:
    point_cloud (open3d.geometry.PointCloud): point cloud with the removed ground plane
    Bool: Denotes the completion of the function

    Description
    Loads a point cloud isolates the ground plane by slicing the point cloud vertically and finding the largest plane, vertically. 
    """
    try:
        z_values = np.asarray(point_cloud.points)[:, 2]
        min_z = np.min(z_values)
        max_z = np.max(z_values)

        for height_threshold in np.linspace(min_z, max_z, num=100):
            mask = z_values >= height_threshold  
            if np.any(~mask): 
                point_cloud.points = o3d.utility.Vector3dVector(np.asarray(point_cloud.points)[mask])
                z_values = z_values[mask]
                break
        return point_cloud, True
    
    except Exception as e:
        logging.error(f"Failed to isolate ground points: {e}")
        return point_cloud, False

def isolation_forest_step(point_cloud, contamination=0.12):
    """
    Parameters:
    point_cloud (open3d.geometry.PointCloud): The input point cloud.
    contamination (float): Estimated proportion of outliers.

    Returns:
    point_cloud (open3d.geometry.PointCloud): Point cloud after outlier removal.
    Bool: denotes success of the step

    Description:
    Identifies and removes outliers based on the contamination rate.
    """
    logging.info("Attempting a step of Isolation Forest...")
    try:
        xyz = np.asarray(point_cloud.points)
        model = IsolationForest(contamination=contamination)
        model.fit(xyz)
        outliers = model.predict(xyz)
        inliers_mask = outliers > 0
        point_cloud = point_cloud.select_by_index(np.where(inliers_mask)[0])
        return point_cloud, True

    except Exception as e:
        logging.error(f"Failed step of Isolation Forest: {e}")
        return point_cloud, False

    
def remove_outliers_isolation_forest(point_cloud, num_iterations=12, contamination=0.12):
    """
    Parameters:
    point_cloud (open3d.geometry.PointCloud): The input point cloud.
    num_iterations (int): Number of iterations to refine outlier removal.
    contamination (float): Estimated proportion of outliers in each iteration.

    Returns:
    point_cloud (open3d.geometry.PointCloud): Processed point cloud with outliers removed.
    Bool: Denotes successfull completion of the function

    Description:
    Refines the point cloud by repeatedly removing outliers with the Isolation Forest algorithm in isolation_forest_step()
    """
    logging.info("Attempting Isolation Forest...")
    success_flag = True
    for iteration in range(num_iterations):
        try:
            point_cloud, success_flag = isolation_forest_step(point_cloud, contamination)
            if not success_flag:
                break 
            
        except Exception as e:
            logging.error(f"Failed Isolation Forest: {e}")
            break 
    logging.info("Iterative Isolation Forest Stage Completed")
    return point_cloud, success_flag

def keep_only_largest_cluster(point_cloud, eps=0.05, min_points=10):
    """
    Parameters:
    point_cloud (open3d.geometry.PointCloud): The point cloud to process.
    eps (float): Maximum distance between two data points for neighborhood.
    min_points (int): Minimum number of points considered as a cluster.

    Returns:
    point_cloud (open3d.geometry.PointCloud): The point cloud after keeping only the largest cluster.
    Bool: Denotes completion of the function
    
    Description:
    Applies DBSCAN clustering to a point cloud, keeping only the largest cluster and saves the intermediate state.
    """
    logging.info("Attempting DBSCAN...")
    try:
        labels = np.array(point_cloud.cluster_dbscan(eps=eps, min_points=min_points, print_progress=True))
        largest_cluster_idx = np.argmax(np.bincount(labels[labels >= 0]))
        largest_cluster_indices = np.where(labels == largest_cluster_idx)[0]
        point_cloud = point_cloud.select_by_index(largest_cluster_indices)
        return point_cloud, True

    except Exception as e:
        logging.error(f"Failed DBSCAN: {e}")
        return point_cloud, False
    
