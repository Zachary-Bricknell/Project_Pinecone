import psycopg2
import open3d as o3d
import numpy as np
from datetime import datetime
import logging
from utils.config import DB_CRED  # Import the database credentials
from utils.file_operations import setup_logging
import os


def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database using credentials from the DB_CRED configuration.

    Returns:
    A psycopg2 connection object to the database.
    """
    try:
        # Use the credentials from DB_CRED dictionary
        conn_str = f"dbname='{DB_CRED['dbname']}' user='{DB_CRED['user']}' host='{DB_CRED['host']}' password='{DB_CRED['password']}' port='{DB_CRED['port']}'"
        return psycopg2.connect(conn_str)
    except Exception as e:
        logging.exception("Failed to connect to the database")
        raise e

def import_to_db(xyz_file_path, table_name, geometry_col_name, additional_data={}):
    """
    Import XYZ data into a PostgreSQL database table as a single MULTIPOINTZ geometry,
    along with additional data.
    
    Parameters:
    - xyz_file_path: Path to the XYZ file containing point cloud data.
    - table_name: Name of the database table.
    - geometry_col_name: Name of the column to store the MULTIPOINTZ geometry.
    - additional_data: Dictionary containing any additional column-value pairs to be inserted.
    """
    base_log_filename = os.path.splitext(os.path.basename(xyz_file_path))[0]
    log_directory = os.path.join(os.path.dirname(xyz_file_path), "logs")

    # Ensure the log directory exists
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)


    setup_logging(base_log_filename,log_directory)

    logging.info("Starting import_to_db function")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Read point cloud and convert to numpy array
        point_cloud = o3d.io.read_point_cloud(xyz_file_path)
        points = np.asarray(point_cloud.points)

        # Construct MULTIPOINTZ WKT string
        multipointz_wkt = "MULTIPOINT Z(" + ", ".join([f"{x} {y} {z}" for x, y, z in points]) + ")"
        
        # Prepare SQL query and data
        columns = [geometry_col_name] + list(additional_data.keys())
        values = [f"SRID=4326;{multipointz_wkt}"] + list(additional_data.values())
        placeholders = ["%s"] * len(values)  # Create placeholders for psycopg2
        
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)}) RETURNING id;"
        
        cursor.execute(query, values)
        inserted_id = cursor.fetchone()[0]  # Fetch the ID of the newly inserted row
        conn.commit()

        print(f"Successfully imported XYZ data to table {table_name}, inserted row ID: {inserted_id}")
    except Exception as e:
        print(f"Failed to import XYZ data to table {table_name}")
    finally:
        cursor.close()
        conn.close()


    return inserted_id  # Return the ID of the inserted row for further reference

def delete_tree(tree_name):
    """
    created by chatgpt
    Deletes a tree record by its name.

    Parameters:
    - tree_name (str): The name of the tree to be deleted.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # First, optionally check if the tree exists and log its existence
        cursor.execute("SELECT id FROM trees WHERE name = %s;", (tree_name,))
        tree_result = cursor.fetchone()
        if tree_result:
            logging.info(f"Tree named '{tree_name}' found with ID: {tree_result[0]}")
            
            # Proceed to delete. This example assumes cascading deletes are handled by the DB schema.
            # If not, you would first manually delete related records in other tables before this step.
            cursor.execute("DELETE FROM trees WHERE name = %s;", (tree_name,))
            conn.commit()
            
            logging.info(f"Tree named '{tree_name}' and its related records have been successfully deleted.")
        else:
            logging.warning(f"No tree found with the name '{tree_name}'. No action taken.")
    except Exception as e:
        logging.exception(f"Error occurred while attempting to delete tree named '{tree_name}'.")
        conn.rollback()  # Roll back in case of error
    finally:
        cursor.close()
        conn.close()

def upload_tree_and_raw_scan(xyz_file_path, tree_name):
    """
    Uploads a raw scan of a tree to the database and creates or updates the tree record.

    Parameters:
    - xyz_file_path (str): The file path of the raw scan (XYZ file).
    - tree_name (str): The name of the tree associated with the raw scan.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if a tree with the given name already exists
        cursor.execute("SELECT id FROM trees WHERE name = %s;", (tree_name,))
        tree_result = cursor.fetchone()
        if not tree_result:
            table_name = "raw_lidar"
            geometry_col_name = "raw_scan"
            additional_data = {"created": datetime.now()}
            # Upload the scan
            raw_lidar_id = import_to_db(xyz_file_path, table_name, geometry_col_name, additional_data)
            cursor.execute("INSERT INTO trees (name,raw_lidar_id) VALUES (%s,%s) RETURNING id;", (tree_name,raw_lidar_id))
            tree_id = cursor.fetchone()[0]
            conn.commit()
            logging.info(f"New tree {tree_name} created with raw_lidar_id {raw_lidar_id}")
        else:
            logging.warning(f"Tree with name {tree_name} already exists.")
    except Exception:
        logging.exception(f"Failed to upload tree and raw scan for {tree_name}")
    finally:
        cursor.close()
        conn.close()

    return raw_lidar_id, tree_id


def download_scan_by_tree_name(tree_name, scan_type, output_file_path):
    """
    Fetches a specified type of scan geometry associated with a given tree name and saves it to an XYZ file.

    Parameters:
    - tree_name (str): The name of the tree whose scan is to be downloaded.
    - scan_type (str): Type of scan to download ('raw', 'cleaned', or 'preprocessed').
    - output_file_path (str): The path to save the downloaded XYZ file.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
         # Determine the correct table and column based on the scan type
        if scan_type == "raw":
            table_column = "raw_scan"
            table_name = "raw_lidar"
        elif scan_type == "cleaned":
            table_column = "cleaned_scan"
            table_name = "cleaned_tree" 
        elif scan_type == "preprocessed":
            table_column = "preprocessed_scan"
            table_name = "preprocessed_tree"
        else:
            print(f"Invalid scan type: {scan_type}")
            return

        # Construct and execute the query
        cursor.execute(f"""
        SELECT ST_AsText({table_column}) 
        FROM {table_name}
        WHERE id IN (
            SELECT {table_name}_id 
            FROM trees 
            WHERE name = %s
        );""", (tree_name,))
        result = cursor.fetchone()

        # Handle the result and write to file
        if result:
            multipointz_wkt = result[0]
            with open(output_file_path, 'w') as file:
                # Parse and write each point to the file
                # Assume multipointz_wkt is like 'MULTIPOINT Z((x y z),(x y z),(x y z))'
                points_str = multipointz_wkt[17:-5]  # This removes the 'MULTIPOINT Z(' prefix and ')' suffix
                points = points_str.split('),(')
                for point_str in points:
                    point_str_cleaned = point_str.strip('()')  # Remove any surrounding parentheses
                    x, y, z = point_str_cleaned.split(' ')  # Now split by spaces
                    file.write(f"{x} {y} {z}\n")
        else:
            print(f"No {scan_type} scan found for the specified tree name.")

        logging.info(f"MULTIPOINTZ geometry written to {output_file_path}.")
    except Exception as e:
        logging.exception(f"Failed to download scan for tree {tree_name}")
    finally:
        cursor.close()
        conn.close()

def fetch_tree_names():
    """Fetch a list of tree names or identifiers from the database."""
    try:
# created by chatgpt
        conn = get_db_connection()
        cursor = conn.cursor()

        # Adjust the query according to your database schema
        cursor.execute("SELECT DISTINCT name FROM trees")
        tree_names = [row[0] for row in cursor.fetchall()]

        logging.info("Successfully fetched tree names.")
    except Exception:
        logging.exception("Failed to fetch tree names")
    finally:
        cursor.close()
        conn.close()


    return tree_names

def link_scan_to_tree(tree_name, scan_id, scan_type):
    """
    Links a scan (cleaned or preprocessed) to an existing tree in the database,
    or creates a new tree entry if needed.
    
    Parameters:
    - tree_name (str): The name of the tree.
    - scan_id (int): The ID of the scan in the respective table (cleaned_tree or preprocessed_tree).
    - scan_type (str): The type of the scan ('cleaned_tree_id' or 'preprocessed_tree_id').
   
    Returns:
    The ID of the tree record in the 'trees' table that was linked to the scan.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check for an existing tree by name
        cursor.execute("SELECT id FROM trees WHERE name = %s;", (tree_name,))
        tree_result = cursor.fetchone()

        if tree_result:
            # Tree exists, update its corresponding scan ID based on scan_type
            tree_id = tree_result[0]
            cursor.execute(f"UPDATE trees SET {scan_type} = %s WHERE id = %s;", (scan_id, tree_id))
        else:
            # Tree does not exist, create a new entry and link the scan
            cursor.execute(f"INSERT INTO trees (name, {scan_type}) VALUES (%s, %s) RETURNING id;", (tree_name, scan_id))
            tree_id = cursor.fetchone()[0]
        conn.commit()
        logging.info(f"Linked scan {scan_id} of type {scan_type} to tree {tree_name}")
    except Exception:
        logging.exception(f"Failed to link scan {scan_id} of type {scan_type} to tree {tree_name}")
    finally:
        cursor.close()
        conn.close()

    return tree_id

def upload_preprocessed_tree_data(tree_name, volume, height, dbh, filepath):
    """
    Updates or creates a preprocessed_tree record with specified data, linking it to a tree record.

    Parameters:
    - tree_name (str): The name of the tree.
    - volume (float): The volume of the tree calculated from the preprocessed scan.
    - height (float): The height of the tree calculated from the preprocessed scan.
    - dbh (float): The diameter at breast height calculated from the preprocessed scan.
    - filepath (str): The file path of the preprocessed scan.

    Returns:
    The ID of the preprocessed_tree record that was updated or created.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Attempt to find the tree in the trees table
    cursor.execute("SELECT id FROM trees WHERE name = %s;", (tree_name,))
    tree_result = cursor.fetchone()

    if tree_result:
        tree_id = tree_result[0]
    else:
        # If tree does not exist, insert it and get the id
        cursor.execute("INSERT INTO trees (name) VALUES (%s) RETURNING id;", (tree_name,))
        tree_id = cursor.fetchone()[0]
        conn.commit()

    cursor.execute("SELECT preprocessed_tree_id FROM trees WHERE id = %s;", (tree_id,))
    preprocessing_tree_id_result = cursor.fetchone()
    if preprocessing_tree_id_result and preprocessing_tree_id_result[0]:
        preprocessing_tree_id = preprocessing_tree_id_result[0]
        # Update the existing preprocessed_tree record with new values
        cursor.execute(
            "UPDATE preprocessed_tree SET height = %s, dbh = %s, volume = %s WHERE id = %s;",
            (height, dbh, volume, preprocessing_tree_id))
    else:
        # Insert into preprocessed_tree if it doesn't exist
        cursor.execute(
            "INSERT INTO preprocessed_tree (preprocessing_scan, height, dbh, volume, created) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
            (filepath, height, dbh, volume, datetime.now()))
        preprocessing_tree_id = cursor.fetchone()[0]
        # Link the new preprocessed_tree record with the tree
        cursor.execute(
            "UPDATE trees SET preprocessed_tree_id = %s WHERE id = %s;",
            (preprocessing_tree_id, tree_id))
        conn.commit()

    conn.commit()
    cursor.close()
    conn.close()
    return preprocessing_tree_id

def upload_cookie_data(tree_name, measurements):
    """
    Inserts multiple 'cookie' records into the database, each representing a cross-section measurement of a tree.

    Parameters:
    - tree_name (str): The name of the tree to which these cookie measurements belong.
    - measurements (list of tuples): Each tuple contains two floats, representing the height and diameter of a tree at a specific point.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

     # First, find the tree_id using the tree_name
    cursor.execute("SELECT id FROM trees WHERE name = %s;", (tree_name,))
    result = cursor.fetchone()
    if result:
        tree_id = result[0]
        for measurement in measurements:
            height, diameter = measurement
            cursor.execute(
                "INSERT INTO cookie (tree_id, diameter, height) VALUES (%s, %s, %s);",
                (tree_id, diameter, height))
        conn.commit()
    else:
        logging.error(f"No tree found with the name '{tree_name}', unable to upload cookie data.")

    conn.commit()
    cursor.close()
    conn.close()
