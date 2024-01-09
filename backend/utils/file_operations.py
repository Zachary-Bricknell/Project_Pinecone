import open3d as o3d
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

def modify_filename(filepath, step):
    """
    Parameters:
    filepath (str): Original file path.
    step (str): The preprocessing step to append (e.g., '1' for pp1).

    Returns:
    str: Modified file path with the updated preprocessing step suffix.
    
    Destription:
    Modifies the filename to update the preprocessing step suffix
    """
    directory, filename = os.path.split(filepath)
    name, ext = os.path.splitext(filename)
    
    # Find an existing preprocessing step in the filename and remove it
    name_parts = name.split('_pp')
    base_name = name_parts[0]
    
    # Append the new preprocessing step suffix to the base filename
    new_filename = f"{base_name}_pp{step}{ext}"
    new_filepath = os.path.join(directory, new_filename)

    # If the new filepath is different from the original, remove the original file
    if filepath != new_filepath and os.path.exists(filepath):
        os.remove(filepath)

    return new_filepath
