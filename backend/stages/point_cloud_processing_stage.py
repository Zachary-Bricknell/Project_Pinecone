import open3d as o3d
import logging
from utils.point_cloud_utils import calculate_diameter_at_height, get_height

### Added for log testing, remove when implemented ###
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.file_operations import setup_logging

#Currently runs as an individual script for testing. user cleaned tapers or primitive shapes. 

def processing_stage(filepath, log_path):
    """
    Analyzes a tree point cloud to measure the circumference and diameter at various heights by taking in a point cloud of a cleaned tree taper.
    
    Parameters:
    filepath (str): The file path of the point cloud.
    
    Returns:
    List of tuples: Each tuple contains the height at which the measurement was taken, the circumference, the radius, and the diameter at that height.
    """        

    setup_logging("Processing_Stage", log_path)     
    point_cloud = o3d.io.read_point_cloud(filepath)    
    base_height, highest_point, total_height = get_height(point_cloud)
    #DBH Measurments
    DBH = 1.3 
    under_dbh_height = [0.1, 0.5, 0.9]
    
    number_of_cookies = 10
    increment_height = (total_height - DBH) / number_of_cookies
    measurements = []
    current_height = base_height + DBH

    o3d.visualization.draw_geometries([point_cloud])
    # For measurements below DBH
    for heights in under_dbh_height:
        diameter = calculate_diameter_at_height(point_cloud, base_height + heights)
        measurements.append({"height": heights, "diameter": diameter})
    
    # For measurements from DBH upward
    for _ in range(number_of_cookies):
        diameter = calculate_diameter_at_height(point_cloud, current_height)
        measurements.append({"height": current_height-base_height, "diameter": diameter})
        current_height += increment_height
        
    return measurements
          