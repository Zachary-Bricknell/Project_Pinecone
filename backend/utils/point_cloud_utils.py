import os
import open3d as o3d
import numpy as np
from utils.file_operations import modify_filename

# Identification of each stage prefix. 
STAGE_PREFIXES = {
    'cleaning': '_cl',
    'preprocessing': '_pp',
    'processing': '_pr'
}

def get_current_step(filepath):
    """
    Parameters:
    filepath (str): The file path of the point cloud.

    Returns:
    tuple: A tuple containing the stage and the step number, e.g., ('cleaning', 1).
    
    Description:
    Determines the current stage and step from the filename prefix(I.e _cl1 means 'cleaning' step 1).
    """
    stage = 'cleaning' #Default first stage
    step = 0
    for key, prefix in STAGE_PREFIXES.items():
        if prefix in filepath:
            stage = key
            # Extract the step number following the prefix
            step_index = filepath.find(prefix) + len(prefix)
            step = int(filepath[step_index]) if step_index < len(filepath) and filepath[step_index].isdigit() else 0
            break

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
    # Adjust the path to remove the .pp suffix to be able to open regardless of what stage of preprocessing it is on. 
    base_name, ext = os.path.splitext(path)
    if ext.startswith('.pp'):
        # Extract the original extension
        original_ext = os.path.splitext(base_name)[1]
        adjusted_path = base_name + original_ext
    else:
        adjusted_path = path

    point_cloud = o3d.io.read_point_cloud(adjusted_path)
    if point_cloud is None:
        raise ValueError("Could not read point cloud for visualization.")

    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(point_cloud)
    vis.run()
    vis.destroy_window()