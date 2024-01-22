import os
import open3d as o3d
import numpy as np
import time
import logging
from utils.file_operations import modify_filename, setup_logging
from sklearn.ensemble import IsolationForest

def preprocessing_stage(filepath, current_step, stage_prefix, log_path, num_iterations=12):
    """
    Parameters:
    filepath (str): The file path of the input point cloud.
    current_step (int): The current step in the preprocessing process.
    stage_prefix (str): The prefix of the current step.
    num_iterations (int): The number of iterations for machine learning-based outlier removal.

    Returns:
    str: The file path of the final processed point cloud.
    bool: True if the preprocessing is successful, False otherwise.

    Description:
    This function preprocesses a point cloud by applying an iterative Isolation Forest method,
    followed by DBSCAN clustering to eliminate smaller clusters. It maintains consistency with the cleaning_stage approach.
    """
    
    setup_logging("preprocessing_stage", log_path)
    point_cloud = o3d.io.read_point_cloud(filepath)
    done_preprocessing = False
    logging.info("Preprocessing Stage Initiated")

    if current_step == 0:
        filepath, success_flag = iterative_isolation_forest(point_cloud, filepath, stage_prefix, num_iterations)
        if not success_flag:
            logging.error("Error in iterative isolation forest stage.")
            return filepath, False
    current_step = 1
    filepath = modify_filename(filepath, stage_prefix, current_step)

    if current_step == 1:
        try:
            logging.info("Applying DBSCAN clustering.")
            filepath = keep_only_largest_cluster(point_cloud, filepath, stage_prefix)
            done_preprocessing = True
        except Exception as e:
            logging.error(f"Error in applying DBSCAN clustering: {e}")

    logging.info("Preprocessing Stage Completed")
    return filepath, done_preprocessing

def remove_outliers_isolation_forest(point_cloud, filepath, contamination=0.12):

    """
    Parameters:
    filepath (str): The file path of the point cloud.
    current_stage_prefix (str): The prefix of the current step.
    contamination (float): Expected proportion of anomalies (outliers) in the data.

    Returns:
    str: Filepath of the point cloud after removing outliers using Isolation Forest.

    Description:
    Removes outliers from a point cloud using the Isolation Forest algorithm and saves the intermediate state.
    """
    
    logging.info("Attempting to remove outliers using Isolation Forest...")
    try:
        xyz = np.asarray(point_cloud.points)
        model = IsolationForest(contamination=contamination)
        model.fit(xyz)
        outliers = model.predict(xyz)
        inliers_mask = outliers > 0
        point_cloud = point_cloud.select_by_index(np.where(inliers_mask)[0])

        o3d.io.write_point_cloud(filepath, point_cloud)
        logging.info("Outliers removed using Isolation Forest.")

        return filepath, True

    except Exception as e:
        logging.error(f"Failed to remove outliers using Isolation Forest: {e}")
        return filepath, False
    
def iterative_isolation_forest(point_cloud, filepath, stage_prefix, num_iterations):
    """
    Parameters:
    filepath (str): The file path of the input point cloud.
    stage_prefix (str): The prefix for this stage.
    num_iterations (int): The number of iterations for Isolation Forest outlier removal.

    Returns:
    str: Filepath of the processed point cloud after iterative outlier removal.

    Description:
    Applies the Isolation Forest outlier removal method iteratively to the point cloud.
    """
    logging.info("Iterative Isolation Forest Stage Initiated")
    success_flag = True
    for iteration in range(num_iterations):
        logging.info(f"Iteration {iteration + 1}: Removing outliers using Isolation Forest.")
        try:
            filepath, success_flag = remove_outliers_isolation_forest(point_cloud, filepath)
            if not success_flag:
                logging.error(f"Failed to complete an iteration...")
                success_flag = False
                break
        except Exception as e:
            logging.error(f"Failed in iteration {iteration + 1} of Isolation Forest: {e}")
            break
    logging.info("Iterative Isolation Forest Stage Completed")
    new_filepath = filepath
    if success_flag:
        new_filepath = modify_filename(filepath, stage_prefix, "1") 
    return new_filepath, success_flag

def keep_only_largest_cluster(point_cloud, filepath, current_stage_prefix, eps=0.05, min_points=10):
    """
    Parameters:
    filepath (str): The file path of the point cloud.
    current_stage_prefix (str): The prefix of the current step.
    eps (float): Maximum distance between two data points for neighborhood.
    min_points (int): Minimum number of points considered as a cluster.

    Returns:
    str: Filepath of the point cloud after keeping only the largest cluster.

    Description:
    Applies DBSCAN clustering to a point cloud, keeping only the largest cluster and saves the intermediate state.
    """
    logging.info("Attempting to keep only the largest cluster using DBSCAN...")
    try:
        labels = np.array(point_cloud.cluster_dbscan(eps=eps, min_points=min_points, print_progress=True))
        largest_cluster_idx = np.argmax(np.bincount(labels[labels >= 0]))
        largest_cluster_indices = np.where(labels == largest_cluster_idx)[0]
        point_cloud = point_cloud.select_by_index(largest_cluster_indices)

        new_filepath = modify_filename(filepath, current_stage_prefix, "2")
        o3d.io.write_point_cloud(new_filepath, point_cloud)
        logging.info("Kept only the largest cluster using DBSCAN.")

        return new_filepath

    except Exception as e:
        logging.error(f"Failed to keep only the largest cluster using DBSCAN: {e}")
        return filepath