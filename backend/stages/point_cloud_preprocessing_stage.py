import os
import open3d as o3d
import numpy as np
import time
import logging
from utils.file_operations import modify_filename, setup_logging
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA


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
        filepath, success_flag = remove_outliers_isolation_forest(filepath, stage_prefix, num_iterations)
        if not success_flag:
            logging.error("Error in iterative isolation forest stage.")
            return filepath, False
        current_step = 1
        filepath = modify_filename(filepath, stage_prefix, current_step)

    if current_step == 1:
        try:
            logging.info("Applying DBSCAN clustering.")
            filepath = keep_only_largest_cluster(filepath, stage_prefix)

            filepath = filter_tree_trunk(filepath, stage_prefix)

            done_preprocessing = True
        except Exception as e:
            logging.error(f"Error in applying DBSCAN clustering: {e}")

    logging.info("Preprocessing Stage Completed")
    return filepath, done_preprocessing

def isolation_forest_step(filepath, contamination=0.12):
    logging.info("Attempting to remove outliers using Isolation Forest...")
    point_cloud = o3d.io.read_point_cloud(filepath)
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

    
def remove_outliers_isolation_forest( filepath, stage_prefix, num_iterations, contamination=0.12):
    logging.info("Iterative Isolation Forest Stage Initiated")
    success_flag = True
    for iteration in range(num_iterations):
        logging.info(f"Iteration {iteration + 1}: Removing outliers using Isolation Forest.")
        try:
            filepath, success_flag = isolation_forest_step(filepath, contamination)
            if not success_flag:
                logging.error("Failed to complete an iteration...")
                break  # Exit the loop if an iteration fails
        except Exception as e:
            logging.error(f"Failed in iteration {iteration + 1} of Isolation Forest: {e}")
            break  # Exit the loop on exception

    logging.info("Iterative Isolation Forest Stage Completed")
    return filepath, success_flag

def keep_only_largest_cluster(filepath, current_stage_prefix, eps=0.05, min_points=10):
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
    point_cloud = o3d.io.read_point_cloud(filepath)
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

def filter_tree_trunk(filepath, stage_prefix, deviation_threshold=0.01, num_segments=10):
    """
    Parameters:
    filepath (str): The file path of the point cloud.
    stage_prefix (str): The prefix of the current step.
    deviation_threshold (float): Threshold for deviation from the main axis. Points with a distance greater than this threshold will be considered as branches.
    num_segments (int): Number of segments to divide the tree trunk along the y-axis.

    Returns:
    str: Filepath of the point cloud after filtering to keep only the trunk of the tree.

    Description:
    Filters the point cloud to keep only the trunk of the tree based on deviation from the main axis obtained through principal component analysis (PCA).
    """
    logging.info("Filtering tree trunk based on deviation from the main axis...")
    point_cloud = o3d.io.read_point_cloud(filepath)
    
    # Convert point cloud to numpy array
    points = np.asarray(point_cloud.points)
    
    # Perform principal component analysis (PCA)
    pca = o3d.geometry.PointCloud().estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=20))
    main_axis = np.asarray(pca.normals)
    
    # Divide the y-axis into segments
    min_y = np.min(points[:, 1])
    max_y = np.max(points[:, 1])
    segment_heights = np.linspace(min_y, max_y, num_segments + 1)
    
    # Create a new file path for the filtered point cloud
    new_filepath = modify_filename(filepath, stage_prefix, "filtered")
    
    # Apply filtering to the entire point cloud
    distances = np.abs(np.dot(points - np.mean(points, axis=0), main_axis))
    trunk_indices = np.where(distances < deviation_threshold)[0]
    trunk_point_cloud = point_cloud.select_by_index(trunk_indices)
    
    # Save the resulting point cloud after filtering
    o3d.io.write_point_cloud(new_filepath, trunk_point_cloud)

    logging.info("Tree trunk filtering based on deviation from the main axis completed.")
    
    return new_filepath
