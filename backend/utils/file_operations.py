import open3d as o3d
import logging
import os
from utils.config import STAGE_PREFIXES

def read_point_cloud(path):
    """
    Parameters:
    path (str): The file path of the point cloud to read.

    Returns:
    open3d.geometry.PointCloud or None: An Open3D point cloud object if successful, None otherwise.
    
    Description:
    Reads an XYZ point cloud from a given file path and converts it into an Open3D point cloud object.

    Supported Filetypes:
    .xyz
    """
    try:
        file_extension = os.path.splitext(path)[1].lower()

        if file_extension == '.xyz':
            return o3d.io.read_point_cloud(path)
        else:
            print(f"Unsupported file format: {file_extension}")
            return None

    except Exception as e:
        print(f"Error reading and converting the point cloud: {e}")
        return None

import os

def modify_filename(filepath, prefix, step):
    """    
    Parameters:
    - filepath (str): The original file path.
    - prefix (str): The new prefix to add or update in the filename.
    - step (str): The step within the processing stage to append.

    Returns:
    - str: The modified file path with the updated or appended prefix and step.
    
    Description:
    Modifies the filename to include a specified processing stage prefix and step, ensuring that any
    existing stage prefixes are removed before adding the new one. If no existing prefix is found,
    the new one is appended.
    
    note: STAGE_PREFIXES from point_cloud_utils.py is used to determine any existing prefix.
    """
    if not os.path.exists(filepath):
        return filepath 

    directory, filename = os.path.split(filepath)
    name, ext = os.path.splitext(filename)
    
    # Remove any existing prefix from the filename
    for _, existing_prefix in STAGE_PREFIXES:
        if existing_prefix in name:
            name = name.split(existing_prefix)[0]
            break  

    #  Append the new filename with updated prefix and step
    new_filename = f"{name}{prefix}{step}{ext}"
    new_filepath = os.path.join(directory, new_filename)

    os.rename(filepath, new_filepath)

    return new_filepath

def setup_logging(log_name, log_path):
    """ 
    Parameters:
    log_name (str): Name of the log file without the ".log" extension.
    log_path (str): Directory path where log file will be saved.

    Returns: None
    
    Description:
    Set up logging configuration to save log messages to a file. uses python logging library to append
    to log file once setup. 
    """
    log_directory = log_path + "/logs"
    os.makedirs(log_directory, exist_ok=True)
    log_file = os.path.join(log_directory, log_name + ".log")
    logging.basicConfig(filename=log_file, 
                        level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')



    
