import open3d as o3d
import numpy as np
from scipy.optimize import least_squares
import logging

### Added for log testing, remove when implemented ###
import os
import sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.file_operations import setup_logging

#Currently runs as an individual script for testing. user cleaned tapers or primitive shapes. 



def calculate_tree_height(filepath):
    """
    Calculate the height of the tree from a point cloud file.

    Parameters:
    filepath (str): The file path of the point cloud.

    Returns:
    float: Height of the tree in meters.
    """
    try:
        point_cloud = o3d.io.read_point_cloud(filepath)
        points = np.asarray(point_cloud.points)
        tree_height = np.max(points[:, 2]) - np.min(points[:, 2])
        return round(tree_height, 2)
    except Exception as e:
        print(f"Failed to calculate tree height: {e}")
        return None


def calculate_diameter_at_height(point_cloud, height):
    """
    Description:
    Calculates the diameter of a tree at a specified height calling sliced_point_cloud at a height, extracting a small sample at that height to fit a circle.

    Parameters:
    point_cloud (open3d.geometry.PointCloud): The original point cloud.
    height (float): The height to obtain the diameter.

    Returns:
    float: The Diameter.
    """
    try:
        # Assuming the tree is upright and Z represents height, slice a thin section around the desired height
        sliced_point_cloud = slice_point_cloud(point_cloud, height - 0.01, height + 0.01)
        if len(sliced_point_cloud.points) == 0:
            return None

        # Project points onto the XY plane and calculate circumference
        points = np.asarray(sliced_point_cloud.points)[:, :2]
        _, _, radius = fit_circle_to_points(points)
        diameter = 2 * radius
        return diameter
    except Exception as e:
        print(f"Failed to calculate diameter: {e}")
        return None

def slice_point_cloud(point_cloud, lower_height, upper_height):
    logging.info("Slicing point cloud between heights {} and {}.".format(lower_height, upper_height))
    points = np.asarray(point_cloud.points)
    sliced_points = points[(points[:, 2] >= lower_height) & (points[:, 2] <= upper_height)]
    if len(sliced_points) == 0:
        logging.warning("No points found in the specified height range.")
    sliced_point_cloud = o3d.geometry.PointCloud()
    sliced_point_cloud.points = o3d.utility.Vector3dVector(sliced_points)
    return sliced_point_cloud


def fit_circle_to_points(points):
    """
    Description:
    Fits a circle to a set of 2D points using least squares optimization.

    Parameters:
    points (numpy array): A 2d array points in the form [[x1, y1], [x2, y2], ...]

    Returns:
    tuple: The center(two values) and the radius.
    """
    try:
        def residuals(params, x, y):
            # for use in the least_squares algorithm to get the residuals of the distance
            xo, yo, r = params
            return np.sqrt((x - xo) ** 2 + (y - yo) ** 2) - r

        # Initialization using averages
        x_mean = np.mean(points[:, 0])
        y_mean = np.mean(points[:, 1])
        initialization = [x_mean, y_mean, np.std(points[:, 0])]

        x = points[:, 0]
        y = points[:, 1]
        result = least_squares(residuals, initialization, args=(x, y))

        xo, yo, radius = result.x
        return xo, yo, radius
    except Exception as e:
        print(f"Failed to fit circle to points: {e}")
        return None

def split_thirteen_cookie(filepath, current_step, stage_prefix):
    """
    This method calculates the height of the tree from a point cloud.
    It splits the tree into 13 equal cookies and counts the height after 1.3m from the ground.

    Parameters:
        filepath (str): The file path of the point cloud.

    Returns:
        float: Height of the tree in meters.
    """
    try:
        point_cloud = o3d.io.read_point_cloud(filepath)
        points = np.asarray(point_cloud.points)
        tree_height = np.max(points[:, 2]) - np.min(points[:, 2])

        # Define heights for the first four cookies
        cookie_heights = [0.1, 0.5, 0.9, 1.3]
        num_cookies = 13
        height_above_ground = 0  # Initialize height above ground starting from 0
        cookie_count = 1

        recorded_heights = []

        while cookie_count <= num_cookies:
            if cookie_count <= 4:
                # Calculate diameter for cookies 1-4
                diameter = calculate_diameter_at_height(point_cloud, cookie_heights[cookie_count - 1])
                if diameter is not None:
                    print(
                        f"\nDiameter at cookie {cookie_count}: {round(diameter, 2)} meters, cookie located at height {round(cookie_heights[cookie_count - 1], 2)} meters")
                # Increment height for next cookie
                height_above_ground = cookie_heights[cookie_count - 1]
                recorded_heights.append(height_above_ground)  # Recording the heights
                cookie_count += 1

            else:
                remaining_height = tree_height - 1.3
                increment = remaining_height * 0.10  # 10% increment
                height_above_ground += increment

                # making sure that the height does not exceed total tree height
                height_above_ground = min(height_above_ground, tree_height)

                # Calculate diameter for cookies 5-13
                diameter = calculate_diameter_at_height(point_cloud, height_above_ground)
                if diameter is not None:
                    print(
                        f"\nDiameter at cookie {cookie_count}: {round(diameter, 2)} meters, cookie located at height {round(height_above_ground, 2)} meters")
                recorded_heights.append(height_above_ground)  # Recording the heights
                cookie_count += 1

        print(f"\ntotal recorded heights: {len(recorded_heights)}")

        return recorded_heights
    except Exception as e:
        print(f"Error in split_thirteen_cookie: {e}")
        return None


def processing_stage(filepath, current_step, stage_prefix, log_path=None):
    
    print("\nEntering processing stage...")
    
    """
    Parameters:
    Description:
    This function processes a point cloud by calculating the height of the tree.
    It splits the tree into 13 equal segments ("cookies") and calculates the height 
    after 1.3m from the ground. The function returns the file path of the processed 
    point cloud and a boolean indicating the success of the operation.
    """
    if log_path:
        log_path = os.path.join(log_path, "processing_log.txt")
    
    try:
        # Start timing the processing stage
        startTime = time.time()

        # Read point cloud
        point_cloud = o3d.io.read_point_cloud(filepath)
        
        # Calculate tree height
        tree_height = calculate_tree_height(filepath)
        tree_diameter = calculate_diameter_at_height(point_cloud, tree_height)
 
        print(f"\nCalculated Tree Height: {tree_height} meters\n")
        
        # Split tree into cookies and calculate diameters
        split_cookies = split_thirteen_cookie(filepath,current_step,stage_prefix)
        for i, height in enumerate(split_cookies):
            tree_diameter = calculate_diameter_at_height(point_cloud, height)
            print(f"Cookie {i+1} height: {round(height, 2)} meters and diameter is {tree_diameter}")

       
        if log_path is not None:
            with open(log_path, 'a') as log_file:
                log_file.write(f"\nCalculated Tree Height: {tree_height} meters\n")
                log_file.write(f"\nTree diameter and 13 cookies are : {tree_diameter}\n")

        # Processing stage completion time
        endTime = time.time()
        totalTime = endTime - startTime
        print(f"\nTotal time needed for the tree height calculation: {totalTime}\n")

       
        return filepath, True

    except Exception as e:
        print(f"Exception occurred: {e}")
       
        if log_path is not None:
            with open(log_path, 'a') as log_file:
                log_file.write(f"Error during tree height calculation: {e}\n")
        return filepath, False
