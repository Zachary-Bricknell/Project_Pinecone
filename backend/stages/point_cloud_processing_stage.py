import open3d as o3d
import numpy as np
from scipy.optimize import least_squares
import logging

### Added for log testing, remove when implemented ###
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.file_operations import setup_logging

#Currently runs as an individual script for testing. user cleaned tapers or primitive shapes. 



def analyze_tree(filepath, log_path):
    """
    Analyzes a tree point cloud to measure the circumference and diameter at various heights by taking in a point cloud of a cleaned tree taper.
    
    Parameters:
    filepath (str): The file path of the point cloud.
    
    Returns:
    List of tuples: Each tuple contains the height at which the measurement was taken, the circumference, the radius, and the diameter at that height.
    """
    setup_logging("cleaning_stage", log_path)     

    point_cloud = o3d.io.read_point_cloud(filepath)
    
    z_values = np.asarray(point_cloud.points)[:, 2]
    base_height = np.min(z_values)  # Accounts for offsets in points not beginning at exactly [0,0,0].
    highest_point = np.max(z_values)
    total_height = highest_point - base_height
    DBH = 1.3 # Standard Diameter Breast Height.
    increment_height = (total_height - DBH) / 100
    measurements = []
    current_height = base_height + DBH
    
    ###For testing###
    current_height = base_height
    increment_height = 1
    

    for _ in range(90):  # Iterate 9 times to cover the tree above DBH
        upper_height = current_height + increment_height
        upper_height = min(upper_height, highest_point)

        sliced_point_cloud = slice_point_cloud(point_cloud, current_height, upper_height)

        circumference, xo, yo, radius = calculate_circumference_of_cylinder(sliced_point_cloud)
        diameter_at_upper_height = calculate_diameter_at_height(point_cloud, upper_height)
        measurements.append((upper_height - base_height, circumference, radius, diameter_at_upper_height))
        
        # Prepare for next iteration
        current_height = upper_height
    
    return measurements

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
        logging.info("Attempting fit_circle_to_points()...")
        def residuals(params, x, y):
            # for use in the least_squares algorithm to get the residuals of the distance 
            # https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html#scipy.optimize.least_squares 
            xo, yo, r = params
            return np.sqrt((x - xo)**2 + (y - yo)**2) - r
        # Initialization using averages
        x_mean = np.mean(points[:, 0])
        y_mean = np.mean(points[:, 1])
        initialization = [x_mean, y_mean, np.std(points[:, 0])]

        x = points[:, 0]
        y = points[:, 1]
        result = least_squares(residuals, initialization, args=(x, y))

        xo, yo, radius = result.x
        logging.info(f"Extracted radius {radius} at {xo}, {yo}")
        return xo, yo, radius
    except Exception as e:
        logging.error(f"Failed to radius: {e}")
        return 
        

def calculate_circumference_of_cylinder(sliced_point_cloud):
    """
    Description:
    Calculates the circumference of a cylinder by fitting a circle to the projected points on the XY plane.

    Parameters:
    sliced_point_cloud (open3d.geometry.PointCloud): A point cloud object containing just the cylinder to be calculated.
    
    Returns:
    tuple: The circumference of the fitted cylinder, center(two values), and the radius.
    """
    try:
        logging.info("Attempting caclulate_circumference_of_cylinder()...")
        # Project the points onto the XY plane
        points = np.asarray(sliced_point_cloud.points)
        projected_points = points[:, :2] #Only the x and Y points

        xo, yo, radius = fit_circle_to_points(projected_points)

        circumference = 2 * np.pi * radius
        logging.info(f"Extracted radius {radius} and circumference{circumference}")
        return circumference, xo, yo, radius

    except Exception as e:
        logging.error(f"Failed to radius: {e}")
        return 

def slice_point_cloud(point_cloud, lower_height, upper_height):
    """
    Slices a point cloud based ont he lower and upper bound

    Parameters:
    point_cloud (open3d.geometry.PointCloud): The original point cloud.
    lower_height (float): The lower bound for height.
    upper_height (float): The upper bound for height.

    Returns:
    open3d.geometry.PointCloud: A new point cloud containing only the points within the specified height range.
    """
    try:
        logging.info("Attempting slice_point_cloud()...")
        points = np.asarray(point_cloud.points)
    
        # Filter based on the height
        sliced_points = points[(points[:, 2] >= lower_height) & (points[:, 2] <= upper_height)]

        sliced_point_cloud = o3d.geometry.PointCloud()
        sliced_point_cloud.points = o3d.utility.Vector3dVector(sliced_points)
    
        logging.info(f"Sliced the point cloud at {lower_height} and {upper_height}")
        return sliced_point_cloud
    except Exception as e:
        logging.error(f"Failed to slice point cloud: {e}")
        return 


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
        logging.info("Attempting calculate_diameter_at_height()...")
        # Assuming the tree is upright and Z represents height, slice a thin section around the desired height
        sliced_point_cloud = slice_point_cloud(point_cloud, height - 0.01, height + 0.01)
        if len(sliced_point_cloud.points) == 0:
            logging.warning("No points found at the specified height. Returning 0 for diameter.")
            return

        # Project points onto the XY plane and calculate circumference
        points = np.asarray(sliced_point_cloud.points)[:, :2]
        _, _, radius = fit_circle_to_points(points)
        diameter = 2 * radius
        logging.info(f"Extracted diameter {diameter} from the point cloud")
        return diameter
    except Exception as e:
        logging.error(f"Failed to calculate diameter: {e}")
        return 


#filepath = r"G:\trentu\pinecone\Project_Pinecone\sample_data\pinecone\w07-2018-tree272_pr0.xyz" #Tree
filepath = r"G:\trentu\pinecone\Project_Pinecone\sample_data\Cone.xyz" #Cone
#filepath = r"G:\trentu\pinecone\Project_Pinecone\sample_data\cylinder.xyz" #Cylinder
log_path = r"G:\trentu\pinecone\Project_Pinecone\sample_data\pinecone\logs"
measurements = analyze_tree(filepath, log_path)


for measurement in measurements:
    print(f"Height: {measurement[0]:.2f} m,  Avg Diameter: {measurement[2]*2:.5f} m, Constrained Diameter {measurement[3]:.5f}")

