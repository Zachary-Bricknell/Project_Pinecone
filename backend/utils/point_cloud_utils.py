from ast import Not
import os
import open3d as o3d
import numpy as np
import logging
from utils.file_operations import modify_filename
from utils.config import STAGE_PREFIXES
from scipy.optimize import least_squares

def get_current_step(filepath):
    """
    Parameters:
    - filepath (str): The file path of the point cloud.

    Returns:
    - tuple: A tuple containing the stage name and the step number such as: ('cleaning', 1).
    
    Description:
    Determines the current stage and step from the filename based on predefined prefixes and the preceeding integer for the step.
    """
    
    # Default to the first stage if no specific prefix is found in the filename
    stage = STAGE_PREFIXES[0][0]
    step = 0

    # Iterate through predefined stage prefixes to identify the current stage and step
    for stage_name, prefix in STAGE_PREFIXES:
        if prefix in filepath:
            stage = stage_name  # Update to the found stage

            step_index = filepath.find(prefix) + len(prefix)
            
            # Extract and convert the step number to ensure it's a digit. 
            step_string = ''.join(char for char in filepath[step_index:] if char.isdigit())
            step = int(step_string) if step_string else 0  # Default to 0 if no digits found
            
            break  # Stop searching once the first matching prefix is found

    return stage, step


def visualize_point_cloud(path, origin_path = None):
    """
    Parameters:
    path (str): The file path of the point cloud to visualize.
    origin_path: This is another path of a point cloud(The oroginal) to visualize alongside the new one.

    Returns: 
    none
    
    Description:
    Opens and visualizes a point cloud from a given file path, or a comparison of two point clouds.
    """
    try:
        point_cloud = o3d.io.read_point_cloud(path)
        if not point_cloud.has_points():
            raise ValueError("The point cloud is empty.")
    except Exception as e:
        raise ValueError(f"Could not read point cloud for visualization: {e}")

    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name="Project Pinecone Visualizer", width=1920, height=1080)

    point_cloud_color = [0.5, 0.5, 0.5] 
    point_cloud.colors = o3d.utility.Vector3dVector([point_cloud_color for i in range(len(point_cloud.points))])
    vis.add_geometry(point_cloud)

    # Check and add a second point cloud if the path is provided, appending it bseide the previous point cloud for a comparison
    if origin_path is not None:
        try:
            new_point_cloud = o3d.io.read_point_cloud(origin_path)
            if not new_point_cloud.has_points():
                raise ValueError("The second point cloud is empty.")

            # Matrix to move the second point cloud for comparison
            translation = np.array([[1, 0, 0, 5],  # distance on the x axis away from the first point cloud
                                    [0, 1, 0, 0],
                                    [0, 0, 1, 0],
                                    [0, 0, 0, 1]])
            new_point_cloud.transform(translation)
            
            new_point_cloud_color = [1, 0, 0]
            new_point_cloud.colors = o3d.utility.Vector3dVector([new_point_cloud_color for i in range(len(new_point_cloud.points))])

            vis.add_geometry(new_point_cloud)
        except Exception as e:
            print(f"Could not read the second point cloud: {e}")
        
    vis.run()
    vis.destroy_window()
    
def get_height(point_cloud):
    """
    description:
    gets the lowest point, highest point, and total hight inbetween based on a numpy array. This accounts for point offsets by using the absolute
    location of the points filtered by its z values
    
    Parameters:
    point_cloud (open3d.geometry.PointCloud): The point cloud to process.
    
    Returns:
    lowest_point(tuple): The absolute lowest point
    highest_point(tuple): The absolute highest point
    total_height(float): The distance in meters, of the two points.
    """
    np_array = np.asarray(point_cloud.points)[:, 2]
    lowest_point = np.min(np_array) 
    highest_point = np.max(np_array)
    total_height = highest_point - lowest_point
    return lowest_point, highest_point, total_height

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
    
        mask = (points[:, 2] >= lower_height) & (points[:, 2] <= upper_height)

        logging.info(f"Sliced the point cloud at {lower_height} and {upper_height}")
        return sliced_point_cloud, mask
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
        # Assuming the tree is upright and Z represents height, slice a thin section around the desired height to use in Cylinder Fitting
        sliced_point_cloud, _ = slice_point_cloud(point_cloud, height - 0.01, height + 0.01)
        if len(sliced_point_cloud.points) == 0:
            logging.warning("No points found at the specified height. Returning 0 for diameter.")
            return

        # Project points onto the XY plane and calculate circumference since Z has been sliced
        points = np.asarray(sliced_point_cloud.points)[:, :2]
        _, _, radius = fit_circle_to_points(points)
        diameter = 2 * radius
        logging.info(f"Extracted diameter {diameter} from the point cloud")
        return diameter
    except Exception as e:
        logging.error(f"Failed to calculate diameter: {e}")
        return
   