import open3d as o3d
import logging
import os
import glob
from utils.config import STAGE_PREFIXES
import logging

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
            logging.error(f"Unsupported file format: {file_extension}")
            return None

    except Exception as e:
        logging.error(f"Error reading and converting the point cloud: {e}")
        return None

import os

def modify_filename(filepath, prefix):
    """    
    Parameters:
    filepath (str): The original file path.
    prefix (str): The new prefix to add or update in the filename.

    Returns:
    str: The modified file path with the updated or appended prefix and step.
    
    Description:
    Modifies the filename to include a specified processing stage prefix, ensuring that any
    existing stage prefixes are removed before adding the new one. If no existing prefix is found,
    the new one is appended.
    """
    directory, filename = os.path.split(filepath)
    name, ext = os.path.splitext(filename)

    # Remove any existing stage prefix from the filename
    for stage_name, existing_prefix in STAGE_PREFIXES:
        # Check and remove existing_prefix if present
        if filename.endswith(existing_prefix + ext):
            name = name[:-len(existing_prefix)]  # Remove the existing prefix from the name
            break

    # Append the new filename with updated prefix
    new_filename = f"{name}{prefix}{ext}"
    new_filepath = os.path.join(directory, new_filename)

    # Renaming the file if it exists; otherwise, just return the new filepath
    if os.path.exists(filepath):
        os.rename(filepath, new_filepath)
    return new_filepath

def write_to_file(point_cloud, filepath, prefix):
    """    
    Parameters:
    point_cloud: The up to date point cloud to be written to new file.
    filepath (str): The original file path.
    prefix (str): The new prefix to add or update in the filename.

    Returns:
    str: The modified file path with the updated or appended prefix and step.
    
    Description:
    his function updates the provided filepath by appending a specified prefix to the filename.
    It then writes the given point cloud data to this new file path, effectively saving the processed
    point cloud under a new name that reflects its last fully completed step
    """
    new_filepath = modify_filename(filepath, prefix)
    o3d.io.write_point_cloud(new_filepath, point_cloud)
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

def find_processed_file(input_filename, search_directory):
    """
    Parameters:
    input_filename (str): The name of the file to search for, extension is allowed.
    search_directory (str): The directory path where the search will be performed.

    Returns:
    str or None: The path to the first matching file found with exact match as input_filename + *. 
    Returns None if no matching file is found.

    Description:
    Removes the extension from the input filename and searches the specified directory for 
    files that start with the resulting string and followed by any characters.
    """
    try:
        # Remove any extension from the input filename
        file_to_search = os.path.splitext(input_filename)[0]
        pattern = os.path.join(search_directory, file_to_search + '*')
        matching_files = glob.glob(pattern)
    
        # Filter out directories
        matching_files = [f for f in matching_files if os.path.isfile(f)]
        matched_file = matching_files[0] if matching_files else None
        if matched_file is not None:
                logging.info(f"Existing file found at {0}, resuming from this file...", matched_file)
        # Return the first matching file or None if there are no matches. 
        return matched_file
    except Exception as e:
        logging.error(f"Failed to search for an existing processed file - {e}")
        return input_filename




    
