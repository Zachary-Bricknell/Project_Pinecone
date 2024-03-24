import os
import sys
import open3d as o3d
import numpy as np
import time
import logging
from utils.file_operations import setup_logging, write_to_file
from sklearn.ensemble import IsolationForest

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
    
from utils.point_cloud_utils import get_height, slice_point_cloud, fit_circle_to_points 

# Map of the order of functions for this stage with the value being the name of the function to be called
# Parameters can be updated here which will be passed into the function
preprocessing_operations = {
    0: {'function': 'ground_segmentation', 'params': {}},
    1: {'function': 'remove_outliers_isolation_forest', 'params': {'num_iterations': 12}},
    2: {'function': 'keep_only_largest_cluster', 'params': {}},
    3: {'function': 'reduce_branches', 'params': {}},
}

def preprocessing_stage(filepath, log_path):
    """        
    Description:
    This driver function preprocesses a point cloud by using various pre-defined, and custom functions to 
    reduce what we define as "noise" to produce as close to a tree taper as we can. 
    
    Parameters:
    filepath (str): The file path of the input point cloud.
    log_path (str): The path to store log files.

    Returns:
    new_filepath (str): The file path of the final processed point cloud.
    bool: True if the preprocessing is successful, False otherwise.
    """
    logging.info("Preprocessing Stage Initiated")
    point_cloud = o3d.io.read_point_cloud(filepath)

    for current_step, operation_info in preprocessing_operations.items():
        operation_function = globals()[operation_info['function']]
        operation_params = operation_info['params']

        try:
            # Execute the preprocessing function with parameters unpacked
            if operation_params:
                point_cloud, success_flag = operation_function(point_cloud, **operation_params)
            else:
                point_cloud, success_flag = operation_function(point_cloud)
                
            if not success_flag:
                logging.error(f"Error in {operation_info['function']}, exiting...")
                return None
                
        except Exception as e:
            logging.error(f"Error in {operation_info['function']}: {e}")
            return None

    # After completing all steps, update the filename to reflect preprocessing completion and write the updated point cloud
    new_filepath = write_to_file(point_cloud, filepath,"_pp")
    logging.info("Preprocessing Stage Completed successfully.")
    return new_filepath, True

def ground_segmentation(point_cloud):
    """
    Description:
    Loads a point cloud isolates the ground plane by slicing the point cloud vertically and finding the largest plane, vertically. 

    Parameters:
    point_cloud (open3d.geometry.PointCloud): The point cloud to process.

    Returns:
    point_cloud (open3d.geometry.PointCloud): Point cloud with the removed ground plane
    Bool: Denotes the completion of the function
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
    Description:
    Identifies and removes outliers based on the contamination rate.

    Parameters:
    point_cloud (open3d.geometry.PointCloud): The input point cloud.
    contamination (float): Estimated proportion of outliers.

    Returns:
    point_cloud (open3d.geometry.PointCloud): Point cloud after outlier removal.
    Bool: Denotes success of the step
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
    Description:
    Refines the point cloud by repeatedly removing outliers with the Isolation Forest algorithm.

    Parameters:
    point_cloud (open3d.geometry.PointCloud): The input point cloud.
    num_iterations (int, Default = 12): Number of iterations to refine outlier removal.
    contamination (float, Default = 0.12): Estimated proportion of outliers in each iteration.

    Returns:
    point_cloud (open3d.geometry.PointCloud): Processed point cloud with outliers removed.
    Bool: Denotes successful completion of the function
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
    Description:
    Applies DBSCAN clustering to a point cloud, identifying the largest continuous cluster of points

    Parameters:
    point_cloud (open3d.geometry.PointCloud): The point cloud to process.
    eps (float, Default = 0.05): Maximum distance between two data points for neighborhood.
    min_points (int, Default = 10): Minimum number of points considered as a cluster.

    Returns:
    point_cloud (open3d.geometry.PointCloud): The point cloud after keeping only the largest cluster.
    Bool: Denotes completion of the function
    """
    logging.info("Attempting DBSCAN...")
    try:
        labels = np.array(point_cloud.cluster_dbscan(eps=eps, min_points=min_points, print_progress=False))
        largest_cluster_idx = np.argmax(np.bincount(labels[labels >= 0]))
        largest_cluster_indices = np.where(labels == largest_cluster_idx)[0]
        point_cloud = point_cloud.select_by_index(largest_cluster_indices)
        return point_cloud, True

    except Exception as e:
        logging.error(f"Failed DBSCAN: {e}")
        return point_cloud, False
    
def reduce_branches(point_cloud):
    """
    Description:
    Reduces the branches along the tree taper by performing incremental slices and using cylinder fitting
    to determine outliers based on radius from xo and yo. 

    Parameters:
    point_cloud (open3d.geometry.PointCloud): The input point cloud representing a tree taper.

    Returns:
    point_cloud (open3d.geometry.PointCloud): The point cloud with adjusted outliers to be inliers
    Bool: Always returns True to indicate the function has completed successfully.
    """
    num_points = np.asarray(point_cloud.points).shape[0]
    point_cloud.colors = o3d.utility.Vector3dVector(np.tile([0.5, 0.5, 0.5], (num_points, 1)))
    base_height, highest_point, _ = get_height(point_cloud)
    increment_height = 0.5

    for current_height in np.arange(base_height, highest_point, increment_height):
        sliced_point_cloud, _ = slice_point_cloud(point_cloud, current_height, current_height + increment_height)
        projected_points = np.asarray(sliced_point_cloud.points)[:, :2]
        
        if len(projected_points) > 0:
            xo, yo, radius = fit_circle_to_points(projected_points)
            distances = np.sqrt((projected_points[:, 0] - xo) ** 2 + (projected_points[:, 1] - yo) ** 2)
            # find points that are farther than 1.25* the readius to identify outliers, while keeping the trees cone shape in tact
            target_radius = 1.25 * radius
            far_points_indices = np.where(distances > target_radius)[0]

            # Adjust outlier points to be where they should be with respect to xo and yo
            for idx in far_points_indices:
                direction = np.array([projected_points[idx, 0] - xo, projected_points[idx, 1] - yo])
                norm_direction = direction / np.linalg.norm(direction)
                new_position = np.array([xo, yo]) + norm_direction * radius
                # Update the point's position
                projected_points[idx, 0] = new_position[0]
                projected_points[idx, 1] = new_position[1]

            # Update the z values to the original ones
            updated_points = np.hstack((projected_points, np.asarray(sliced_point_cloud.points)[:, 2:]))

            original_points = np.asarray(point_cloud.points)
            mask = (original_points[:, 2] >= current_height) & (original_points[:, 2] <= current_height + increment_height)
            original_points[mask] = updated_points

            point_cloud.points = o3d.utility.Vector3dVector(original_points)
            
    return point_cloud, True