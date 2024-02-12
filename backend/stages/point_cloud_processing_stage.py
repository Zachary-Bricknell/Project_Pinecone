# Left empty as template
import os
import open3d as o3d
import numpy as np
from stages.point_cloud_cleaning_stage import *
import time



def calculate_tree_diameter(filepath, current_step, stage_prefix):

    """ 
    This method calculates the height of the tree from a point cloud .
    as well it splits the tree in 13 equal cookies and counts the height after 1.3m from the ground..."
    
    Parameters:
        filepath (str): The file path of the point cloud.
            
    Returns:
        float: Height of the tree in meters.
 
    """
     
    
    point_cloud = o3d.io.read_point_cloud(filepath)
    points = np.asarray(point_cloud.points)
    tree_height = np.max(points[:, 2]) - np.min(points[:, 2])
    
    #same thing as cookies as in the pdf 13 of them in total
    num_cookies = 13  
    #this is the 1.3 meter from the ground till the 4th cookie basically
    initial_height = 1.3  
    #I am making the each increment to be the 10 percent of the total height of the tree
    increment = tree_height * 0.1  # 10% of the total height
    
    #since we are really starting counting from the 1.3 for the cookies I have assigned the height to start from 1.3 as in the PDF's
    height_above_ground = initial_height  
    #The counter for the cookies starts from 1 not from 0...
    cookie_count = 1
    #flag the 5th cookie to start calculations.(currently just declared and defined)
    reached_fifth_cookie = False

    #Ensure the height above ground is always less than the total tree height, and the cookie count does not exceed 13.
    while height_above_ground < tree_height and cookie_count < num_cookies:
        
        # from 1-4 coockie
        if cookie_count <=4:
            #I am not adjusting the height of the tree but still calculating the diameter currently this is the "placeholder"
            print(f"\ndiameter is at coockie {cookie_count} is: [DIAMETER FORMULA]")
        
        #checking if 5th cookie
        if reached_fifth_cookie:
          #starting from 1.3 meters from ground 10% increase each time
            height_above_ground += increment
            #coockie count + 1
            cookie_count += 1
            # height above ground does not exceed the tree height (min)
            height_above_ground = min(height_above_ground, tree_height) 
            
            #printing information some of the parts are placeholders for the diameter formula                      
            print("\nHeight above ground: {:.2f} meters, Number of cookies: {} and diameter [DIAMETER FORMULA]".format(height_above_ground, cookie_count))
            
        else:
            #if we have not reached the fifth cookie keep going till we will reach.
            cookie_count += 1
            if cookie_count >= 4:
                #turning flag to true after we reach the 5th cookie
                reached_fifth_cookie = True
                  

  
def calculate_tree_height(filepath,current_step, stage_prefix):
  
    
    point_cloud = o3d.io.read_point_cloud(filepath)
    points = np.asarray(point_cloud.points)
    tree_height = np.max(points[:, 2]) - np.min(points[:, 2])
    
                
     #returning the total height of the tree           
    return tree_height






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
