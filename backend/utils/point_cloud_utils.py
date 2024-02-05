from ast import Not
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