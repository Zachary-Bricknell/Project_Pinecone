import os
import open3d as o3d
import numpy as np
from utils.file_operations import modify_filename
from utils.config import STAGE_PREFIXES

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


def visualize_point_cloud(path):
    """
    Parameters:
    path (str): The file path of the point cloud to visualize.

    Returns: 
    none
    
    Description:
    Opens and visualizes a point cloud from a given file path.
    """
    point_cloud = o3d.io.read_point_cloud(path)
    if point_cloud is None:
        raise ValueError("Could not read point cloud for visualization.")
        return

    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(point_cloud)
    vis.run()
    vis.destroy_window()