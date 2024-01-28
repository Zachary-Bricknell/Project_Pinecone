import open3d as o3d
import logging
import os

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

def modify_filename(filepath, prefix, step):
    """
    Parameters:
    filepath (str): Original file path.
    filepath (str): Prefix denoting the stage of processing (e.g _cl = data cleaning)
    step (str): The preprocessing step to append (e.g., '1' for _cl1).

    Returns:
    str: Modified file path with the updated preprocessing step suffix.
    
    Destription:
    Modifies the filename to update the preprocessing step suffix
    """
    directory, filename = os.path.split(filepath)
    name, ext = os.path.splitext(filename)
    
    # Find an existing preprocessing step in the filename and remove it
    name_parts = name.split(prefix)
    base_name = name_parts[0]
    
    # Append the new preprocessing step suffix to the base filename
    new_filename = f"{base_name}{prefix}{step}{ext}"
    new_filepath = os.path.join(directory, new_filename)

    # If the new filepath is different from the original, remove the original file
    if filepath != new_filepath and os.path.exists(filepath):
        os.remove(filepath)
        
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



    
