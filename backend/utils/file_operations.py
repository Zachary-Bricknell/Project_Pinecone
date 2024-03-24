import open3d as o3d
import logging
import os
import glob
from utils.config import STAGE_PREFIXES
import logging

def read_point_cloud(path):
    """
    Description:
    Reads an XYZ point cloud from a given file path and converts it into an Open3D point cloud object.

    Parameters:
    path (str): The file path of the point cloud to read.

    Returns:
    open3d.geometry.PointCloud or None: An Open3D point cloud object if successful, None otherwise.
    
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


def modify_filename(filepath, prefix):
    """    
    Description:
    Modifies the filename to include a specified processing stage prefix, ensuring that any
    existing stage prefixes are removed before adding the new one. If no existing prefix is found,
    the new one is appended.
    
    Parameters:
    filepath (str): The original file path.
    prefix (str): The new prefix to add or update in the filename.

    Returns:
    new_filepath (str): The modified file path with the updated or appended prefix and step.
    """
    
    directory, name, ext = get_base_filename(filepath)
    new_filename = f"{name}{prefix}{ext}"
    new_filepath = os.path.join(directory, new_filename)

    if os.path.exists(filepath):
        os.rename(filepath, new_filepath)
    return new_filepath

def get_base_filename(filepath):
    """
    Description:
    Extracts the filename, extension and directory from the given filepath, removing any suffixes
    
    Parameters:
    filepath(str): Path to the file to split up
    
    Returns:
    directory (str): the directory that the file belongs to
    name (str): Base name of the file
    ext (str): The extension of the file
    """
    directory, filename = os.path.split(filepath)
    name, ext = os.path.splitext(filename)

    for stage_name, existing_prefix in STAGE_PREFIXES:
        if name.endswith(existing_prefix):
            name = name[:-len(existing_prefix)]
            break

    return directory, name, ext

def write_to_file(point_cloud, filepath, prefix):
    """    
    Description:
    This function updates the provided filepath by appending a specified prefix to the filename.
    Uses modify_filename() for the name itself, then writes the given point cloud to that file
    
    Parameters:
    point_cloud (open3d.geometry.PointCloud): The up to date point cloud to be written to new file.
    filepath (str): The original file path.
    prefix (str): The new prefix to add or update in the filename.

    Returns:
    str: The modified file path with the updated or appended prefix and step.
    """
    new_filepath = modify_filename(filepath, prefix)
    o3d.io.write_point_cloud(new_filepath, point_cloud)
    return new_filepath

def setup_logging(log_name, log_path):
    """
    Set up logging configuration to save log messages to a file, creating a new logger for each file processed.

    Parameters:
    filepath (str): The file path of the point cloud, used to generate log file name.
    log_path (str): Directory path where log file will be saved.
    """
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)

    log_directory = os.path.join(log_path, "logs")
    os.makedirs(log_directory, exist_ok=True)
    log_file = os.path.join(log_directory, log_name + ".log")

    # Check if the logger already has handlers to prevent duplicate logs
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def find_processed_file(input_filename, search_directory):
    """
    Description:
    Removes the extension from the input filename and searches the specified directory for 
    files that start with the resulting string and followed by any characters.
    
    Parameters:
    input_filename (str): The name of the file to search for, extension is allowed.
    search_directory (str): The directory path where the search will be performed.

    Returns:
    str or None: The path to the first matching file found with exact match as input_filename + *. 
    Returns None if no matching file is found.
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




    