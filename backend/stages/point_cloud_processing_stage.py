# Left empty as template
import os
import open3d as o3d
import numpy as np
from stages.point_cloud_cleaning_stage import *
import time



def split_thirteen_cookie(filepath, current_step, stage_prefix):
    """ 
    This method calculates the height of the tree from a point cloud.
    It splits the tree into 13 equal cookies and counts the height after 1.3m from the ground.
    
    Parameters:
        filepath (str): The file path of the point cloud.
            
    Returns:
        float: Height of the tree in meters.
    """
    point_cloud = o3d.io.read_point_cloud(filepath)
    points = np.asarray(point_cloud.points)
    tree_height = np.max(points[:, 2]) - np.min(points[:, 2])
    
    # Define heights for the first four cookies
    cookie_heights = [0.1, 0.5, 0.9, 1.3]
    num_cookies = 13
    height_above_ground = 0  # Initialize height above ground starting from 0 , then the first coockie will be coockie_heights[0] - 0.1
    cookie_count = 1
    
    while cookie_count <= num_cookies:
        if cookie_count <= 4:
            # Calculate diameter for cookies 1-4
            diameter = calculate_tree_diameter(filepath, current_step, stage_prefix)
            print(f"\nDiameter at cookie {cookie_count}: {round(diameter,2)} meters, cookie located at height {round(cookie_heights[cookie_count - 1],2)} meters")
            # Increment height for next cookie
            height_above_ground = cookie_heights[cookie_count - 1]
            cookie_count += 1 #1.93537 (round to 2decimals)
        else:
            remaining_height = tree_height-1.3  
            increment = remaining_height * 0.10  # 10% increment 
            height_above_ground += increment
            
            # making sure that the height does not exceed total tree height
            height_above_ground = min(height_above_ground, tree_height)
            
            # Calculate diameter for cookies 5-13 -- currentyl something is wrong with it still figuring it out...
            diameter = calculate_tree_diameter(filepath, current_step, stage_prefix)
            print(f"\nDiameter at cookie {cookie_count}: {round(diameter,2)} meters, cookie located at height {round(height_above_ground,2)} meters")
            cookie_count += 1
    
    return tree_height

                  

def calculate_tree_height(filepath,current_step, stage_prefix):
  
    
    point_cloud = o3d.io.read_point_cloud(filepath)
    points = np.asarray(point_cloud.points)
    tree_height = np.max(points[:, 2]) - np.min(points[:, 2])
    
                
     #returning the total height of the tree           
    return round(tree_height,2)


#It does not work so far, needs to be checked
def calculate_tree_diameter(filepath, current_step, stage_prefix):
    """
    Calculate the diameter of the tree at a height of 1.3m above the ground from a point cloud file.
    
    Parameters:  
       
    Returns:
        
    """
    
    #Issue is in not being able to grab the correct areas for the diameter, each time
    #could be something else 
    #This method is not implemented yet fully only parts of it are, and they are not right, needs to be developed
    
    point_cloud = o3d.io.read_point_cloud(filepath)
    points = np.asarray(point_cloud.points)
    
    # Calculate the tree height and determine the ground level
    
    tree_height = np.max(points[:, 2]) - np.min(points[:, 2])
    ground_level = np.min(points[:, 2])
    
    # Assuming the tree diameter is to be calculated at 1.3m above the ground
    target_height = ground_level + 1.3
    
    
    # if len(slice_points) == 0:
    #     return 0  # No points in the target slice, return 0 as a placeholder
    
    # # Calculate the diameter as the maximum distance between any two points in the slice
    # max_distance = np.max([np.linalg.norm(p1 - p2) for p1 in slice_points for p2 in slice_points])
    
    return target_height



def processing_stage(filepath, current_step, stage_prefix, log_path=None):
    
    print("\nEntering processing stage...")
    
    """
    Parameters:
    filepath (str): The file path of the input point cloud.
    current_step (int): The current step in the processing process.
    stage_prefix (str): The prefix of the current step.
    log_path (str, optional): Path to the log file where processing information will be saved.

    Returns:
    filepath (str): The file path of the processed point cloud after tree height calculation.
    success (bool): True if the processing is successful, False otherwise.

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

        # Calculate tree height
        split_cookies = split_thirteen_cookie(filepath, current_step, stage_prefix)
        tree_height = calculate_tree_height(filepath, current_step, stage_prefix)
        tree_diameter = calculate_tree_diameter(filepath, current_step, stage_prefix)
    
        print(f"\nCalculated Tree Height: {tree_height} meters\n")
        
        # Optionally, log the calculated tree height to a log file
        if log_path is not None:
            with open(log_path, 'a') as log_file:
                log_file.write(f"\nCalculated Tree Height: {tree_height} meters\n")
                log_file.write(f"\nTree diameter and 13 cookies are : {tree_diameter}\n")

        # Processing stage completion time
        endTime = time.time()
        totalTime = endTime - startTime
        print(f"\nTotal time needed for the tree height calculation: {totalTime}\n")

        # For consistency, the filepath is returned unchanged as the operation
        # does not modify the point cloud file itself in this case
        return filepath, True

    except Exception as e:
        print(f"Exception occurred: {e}")
        # Optionally, log the error to the log file
        if log_path is not None:
            with open(log_path, 'a') as log_file:
                log_file.write(f"Error during tree height calculation: {e}\n")
        return filepath, False
