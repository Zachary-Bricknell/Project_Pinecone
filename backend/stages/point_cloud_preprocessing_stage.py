import open3d as o3d
import numpy as np
import logging
from utils.file_operations import modify_filename, setup_logging
from sklearn.ensemble import IsolationForest
from sklearn.ensemble import RandomForestRegressor



def ground_segmentation(filepath, density_radius=0.05):
    """
    Loads a point cloud and iteratively removes points below increasing height thresholds,
    aiming to isolate the ground or lower layers.
    """
    pcd = o3d.io.read_point_cloud(filepath)
    z_values = np.asarray(pcd.points)[:, 2]
    min_z, max_z = np.min(z_values), np.max(z_values)
    
    for height_threshold in np.linspace(min_z, max_z, num=100):
        mask = z_values >= height_threshold
        if np.any(~mask):
            pcd.points = o3d.utility.Vector3dVector(np.asarray(pcd.points)[mask])
            break
    return filepath


def isolation_forest_step(filepath, contamination=0.11):
    """
    Attempt to remove outliers using Isolation Forest.
    """
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

def random_forest_step(filepath, stage_prefix, num_iterations=5, **kwargs):
    """
    Attempt to remove tree noise using Random Forest.
    """
    logging.info("Attempting to remove tree noise using Random Forest...")
    point_cloud = o3d.io.read_point_cloud(filepath)
    success_flag = True
    
    try:
        for iteration in range(num_iterations):
            xyz = np.asarray(point_cloud.points)
            model = RandomForestRegressor(**kwargs)
            model.fit(xyz[:, :2], xyz[:, 2])  # Assuming x and y are used as features
            z_predicted = model.predict(xyz[:, :2])
            residual = np.abs(xyz[:, 2] - z_predicted)
            inliers_mask = residual < np.percentile(residual, 95)  # Adjust the percentile as needed
            point_cloud = point_cloud.select_by_index(np.where(inliers_mask)[0])
            o3d.io.write_point_cloud(filepath, point_cloud)
            logging.info(f"Tree noise removed using Random Forest. Iteration {iteration + 1}")
        
        return filepath, success_flag

    except Exception as e:
        logging.error(f"Failed to remove tree noise using Random Forest: {e}")
        return filepath, False


def remove_outliers_isolation_forest(filepath, stage_prefix, num_iterations, contamination=0.10):
    """
    Iteratively apply Isolation Forest for outlier removal.
    """
    logging.info("Iterative Isolation Forest Stage Initiated")
    success_flag = True

    for iteration in range(num_iterations):
        logging.info(f"Iteration {iteration + 1}: Removing outliers using Isolation Forest.")
        try:
            filepath, success_flag = isolation_forest_step(filepath, contamination)
            if not success_flag:
                logging.error("Failed to complete an iteration...")
                break
        except Exception as e:
            logging.error(f"Failed in iteration {iteration + 1} of Isolation Forest: {e}")
            break

    logging.info("Iterative Isolation Forest Stage Completed")
    return filepath, success_flag


def remove_outliers_random_forest(filepath, stage_prefix, num_iterations, rf_kwargs=None):
    """
    Iteratively apply Random Forest for outlier removal.
    """
    logging.info("Iterative Random Forest Stage Initiated")
    success_flag = True

    for iteration in range(num_iterations):
        logging.info(f"Iteration {iteration + 1}: Removing outliers using Random Forest.")
        try:
            filepath, success_flag = random_forest_step(filepath, stage_prefix, **rf_kwargs)
            if not success_flag:
                logging.error("Failed to complete an iteration...")
                break
        except Exception as e:
            logging.error(f"Failed in iteration {iteration + 1} of Random Forest: {e}")
            break

    logging.info("Iterative Random Forest Stage Completed")
    return filepath, success_flag


def keep_only_largest_cluster(filepath, current_stage_prefix, eps=0.05, min_points=10):
    """
    Keep only the largest cluster using DBSCAN clustering.
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


def read_point_cloud_from_file(filepath):
    """
    Reads a point cloud from a given file path.
    
    Args:
    - filepath: Path to the point cloud file.
    
    Returns:
    - point_cloud: Open3D point cloud object.
    """
    point_cloud = o3d.io.read_point_cloud(filepath)
    return point_cloud


# Define a dictionary to manage pipeline steps
pipeline_steps = {
    0: ("Ground Segmentation", ground_segmentation),
    1: ("Isolation Forest Outlier Removal", remove_outliers_isolation_forest),
    2:("Random Forest Tree Noise Removal",random_forest_step),
    3: ("DBSCAN Clustering", keep_only_largest_cluster)
}

def preprocessing_stage(filepath, current_step, stage_prefix, log_path, num_iterations=14, rf_kwargs=None):
    """
    Process point cloud data through a series of steps for noise reduction and cleaning.
    """
    setup_logging("preprocessing_stage", log_path)
    logging.info("Preprocessing Stage Initiated")
    
    success_flag = True

    while current_step < len(pipeline_steps) and success_flag:
        step_name, step_function = pipeline_steps[current_step]
        logging.info(f"Applying {step_name}.")
        
        try:
            if step_name == "Isolation Forest Outlier Removal":
                filepath, success_flag = step_function(filepath, stage_prefix, num_iterations)
            elif step_name == "Random Forest Tree Noise Removal":
                rf_kwargs = {
                'n_estimators': 60,
                'max_depth': 12,  # Adjust parameters as needed
                # Add more parameters as needed
                }
                filepath, success_flag = step_function(filepath, stage_prefix, **rf_kwargs)
            else:
                filepath = step_function(filepath, stage_prefix if step_name == "DBSCAN Clustering" else None)
            if success_flag:
                logging.info(f"Finished {step_name}.")
                current_step += 1
                filepath = modify_filename(filepath, stage_prefix, current_step)
        except Exception as e:
            logging.error(f"Error in applying {step_name}: {e}")
            success_flag = False

    return filepath, success_flag




