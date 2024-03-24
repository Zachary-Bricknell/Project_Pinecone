import tkinter as tk
from tkinter import filedialog, LabelFrame, ttk, messagebox
import subprocess
import os
import sys
import threading

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.main import process, visualize_point_cloud, process_and_visualize
# Import database utilities
from backend.utils.db_utils import fetch_tree_names, download_scan_by_tree_name, delete_tree

def disable_all_buttons():
    """
    Disable all buttons
    """ 
    browse_button["state"] = "disabled"
    process_button["state"] = "disabled"
    visualize_button["state"] = "disabled"
    process_and_visualize_button["state"] = "disabled"

def enable_all_buttons():
    """
    enables all buttons
    """
    browse_button["state"] = "normal"
    process_button["state"] = "normal"
    visualize_button["state"] = "normal"
    process_and_visualize_button["state"] = "normal"

def wait_while_processing(target_function):
    """
    Decorator function to allow multithreading of the backend processing. Diables all buttons while
    a chile process is running, and re-enables it when the child process is done. Updates the status lable to
    ensure clarity of current process.
    """
    def threading_wrapper():
        def run():
            root.after(0, update_status, "Processing...")
            try:
                target_function()
            finally:
                root.after(0, update_status, "Ready")
                root.after(0, enable_all_buttons)

        disable_all_buttons()
        threading.Thread(target=run).start()
    return threading_wrapper

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("XYZ Files", "*.xyz")])
    if file_path:
        file_path_label.config(text=f"File Path: {file_path}")
        process_button["state"] = "normal"
        visualize_button["state"] = "normal"
        process_and_visualize_button["state"] = "normal"
        process_and_upload_button["state"] = "normal"  
        
        for entry in dbh_height_group + main_taper_group:
            entry.delete(0, tk.END)
        for field in tree_information_fields:
            entries[field].delete(0, tk.END)

@wait_while_processing
def process_file():
    file_path = file_path_label.cget("text").split("File Path: ")[1]
    destination_directory = os.path.join(os.path.dirname(file_path), "pinecone")

    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    processed_file, _ = process(file_path, destination_directory, False)
    update_entries(processed_file)
 
@wait_while_processing
def visualize_file():
    file_path = file_path_label.cget("text").split("File Path: ")[1]
    visualize_point_cloud(file_path)
 
@wait_while_processing
def process_and_visualize_file():
    file_path = file_path_label.cget("text").split("File Path: ")[1]
    destination_directory = os.path.join(os.path.dirname(file_path), "pinecone")
    processed_file = process_and_visualize(file_path, destination_directory)
    update_entries(processed_file)

@wait_while_processing
def process_and_upload_file():
    """
    Processes and uploads the selected point cloud file.
    
    This function is triggered by a button press. It retrieves the path of the selected point cloud file,
    processes it, and then uploads the processed data to the database. Processing includes cleaning,
    preprocessing, and calculating metric data. The function then updates the GUI to display the
    results of the processing.
    
    The processing and upload are done only if the destination directory exists; otherwise, the directory
    is created. The upload_flag is set to True to enable the upload feature during processing.
    """
    file_path = file_path_label.cget("text").split("File Path: ")[1]
    destination_directory = os.path.join(os.path.dirname(file_path), "pinecone")

    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    processed_file, _ = process(file_path, destination_directory, True)
    update_entries(processed_file)

def delete_selected_tree():
    """
    Deletes the selected tree from the database.
    
    This function retrieves the name of the selected tree from the GUI dropdown menu
    and invokes the delete_tree function to remove the tree and its associated data
    from the database. It is triggered by a GUI action, such as pressing a "Delete"
    button.
    """
    selected_tree = tree_name_var.get()
    if selected_tree:
        delete_tree(selected_tree)

def update_tree_dropdown(event=None):
    """
    Updates the tree names dropdown menu in the GUI.
    
    This function fetches the list of tree names from the database and updates
    the dropdown menu to display these names. It can be triggered by various events,
    such as clicking on the dropdown menu, to ensure the list is refreshed and up to date.
    """ 
    tree_names = fetch_tree_names()
    dropdown['values'] = tree_names
    if tree_names:
        dropdown.current(0)
    else:
        dropdown.set('')


def resource_path(relative_path):
    """
    Helper Function for Pyinstaller to find the "resources" folder when packaged
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def update_entries(csv_data):
    """
    Takes the standardized CSV data in list format and updates the GUI entries.

    Parameters:
    csv_data (list): The data from the CSV file as a list.
    """
    for i, field in enumerate(tree_information_fields):
        entries[field].delete(0, tk.END)
        if i == 0:
            # First entry is a string
            entries[field].insert(0, csv_data[i])
        elif i == 3:
            # Fourth entry for volume with "Cubic Meters" suffix
            entries[field].insert(0, "{:.2f} Cubic Meters".format(csv_data[i]))
        else:
            entries[field].insert(0, "{:.2f} M".format(csv_data[i]))

    measurement_start_index = 4
    measurement_pairs = (len(csv_data) - measurement_start_index) // 2

    all_measurement_entries = dbh_height_group + main_taper_group
    measurement_pairs = min(measurement_pairs, len(all_measurement_entries))

    for i in range(measurement_pairs):
        height_index = measurement_start_index + i * 2
        diameter_index = height_index + 1

        # Update each entry with "H: height D: diameter" format
        if height_index < len(csv_data) and diameter_index < len(csv_data):
            entry_text = "H: {:.2f} M  D: {:.2f} M".format(csv_data[height_index], csv_data[diameter_index])
            all_measurement_entries[i].delete(0, tk.END)
            all_measurement_entries[i].insert(0, entry_text)

def update_status(message):
    status_label.config(text=message)

def download_scan_action(scan_type):
    """
    Initiates the download of a specified type of scan for a selected tree.
    
    This function is triggered by a GUI action, typically involving the user selecting a tree and
    a type of scan (e.g., raw, cleaned, preprocessed) to download. The function then:
    - Determines the selected tree based on the GUI dropdown selection.
    - Creates a directory for downloaded files, if it does not already exist.
    - Constructs the path for the output file based on the tree's name and the scan type.
    - Calls a function to fetch and download the specified scan, saving it to the constructed path.
    - Notifies the user of the success or failure of the download operation through message boxes.
    
    Parameters:
    - scan_type (str): The type of scan to download, as specified by the user in the GUI. It could be 'raw', 'cleaned', or 'preprocessed'.

    If no tree is selected, it displays a warning message to the user.
    """
    selected_tree = tree_name_var.get()
    if selected_tree:
        # Create a directory for downloads if it doesn't exist
        download_dir = os.path.join(os.getcwd(), "downloaded_files")
        os.makedirs(download_dir, exist_ok=True)
        
        # Set the output file path using the tree name and scan type
        output_file_path = os.path.join(download_dir, f"{selected_tree}_{scan_type}.xyz")
        
        try:
            download_scan_by_tree_name(selected_tree, scan_type, output_file_path)
            messagebox.showinfo("Download Successful", f"{scan_type.capitalize()} scan for '{selected_tree}' has been downloaded to {output_file_path}.")
        except Exception as e:
            messagebox.showerror("Download Failed", str(e))
    else:
        messagebox.showwarning("No Tree Selected", "Please select a tree to download the scan.")
    
## Tkinter window

root = tk.Tk()
root.title("Pinecone Project")

window_width = 800
window_height = 700
root.geometry(f"{window_width}x{window_height}")

# Create the Notebook widget
notebook = ttk.Notebook(root)
notebook.pack(expand=1, fill="both")

# Create frames for each tab
processing_tab = tk.Frame(notebook)
database_tab = tk.Frame(notebook)

# Add tabs to the notebook
notebook.add(processing_tab, text='Processing')
notebook.add(database_tab, text='Database Operations')

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int((screen_width - window_width) / 2)
center_y = int((screen_height - window_height) / 2)
root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

file_path_frame = tk.Frame(processing_tab)
file_path_frame.pack(side="top", fill="x")

status_label = tk.Label(file_path_frame, text="Ready", font=("Arial", 12))
status_label.pack(side="top", fill="x", pady=10)

file_path_label = tk.Label(file_path_frame, text="File Path:", font=("Arial", 12))
file_path_label.pack(side="top", fill="x", pady=10)

button_frame = tk.Frame(processing_tab)
button_frame.pack(side="top", pady=20)

browse_button = tk.Button(button_frame, text="Browse", command=browse_file, font=("Arial", 12))
browse_button.pack(side="left", padx=10)

process_button = tk.Button(button_frame, text="Process File", command=process_file, font=("Arial", 12), state="disabled")
process_button.pack(side="left", padx=10)

visualize_button = tk.Button(button_frame, text="Visualize File", command=visualize_file, font=("Arial", 12), state="disabled")
visualize_button.pack(side="left", padx=10)

process_and_visualize_button = tk.Button(button_frame, text="Process and Visualize File", command=process_and_visualize_file, font=("Arial", 12), state="disabled")
process_and_visualize_button.pack(side="left", padx=10)

process_and_upload_button = tk.Button(button_frame, text="Process and Upload File", command=process_and_upload_file, font=("Arial", 12), state="disabled")
process_and_upload_button.pack(side="left", padx=10)


# Group box for tree overview
tree_information_group = tk.LabelFrame(processing_tab, text="Tree Information", padx=10, pady=10)
tree_information_group.pack(side="top", fill="x", padx=20, pady=10)

tree_information_fields = ["Tree Name", "Tree Height", "Increment", "Est Volume"]
entries = {}
for i, field in enumerate(tree_information_fields):
    row = i // 2
    col = i % 2
    label = tk.Label(tree_information_group, text=f"{field}:", font=("Arial", 12))
    label.grid(row=row, column=col*2, sticky="e", padx=(5, 2), pady=5)
    entry = tk.Entry(tree_information_group, bg="lightgrey", font=("Arial", 12))
    entry.grid(row=row, column=col*2+1, sticky="ew", padx=(2, 5), pady=5)
    entries[field] = entry

# Configure columns to have uniform weight
tree_information_group.grid_columnconfigure((0, 1), weight=1)

# First group box for DBH entries representing the 3 heights below dbh, and dbh
dbh_group = LabelFrame(processing_tab, text="DBH", padx=10, pady=10)
dbh_group.pack(side="top", fill="x", padx=20, pady=10)

dbh_height_group = []
for i in range(1, 5):
    row = (i-1) // 2
    col = (i-1) % 2
    tk.Label(dbh_group, text=f"Cookie {i}:", font=("Arial", 12)).grid(row=row, column=col*2, sticky="e", padx=(5, 2), pady=5)
    entry = tk.Entry(dbh_group, bg="lightgrey", font=("Arial", 12))
    entry.grid(row=row, column=col*2+1, sticky="ew", padx=(2, 5), pady=5)
    dbh_height_group.append(entry)

# Configure columns to have uniform weight
dbh_group.grid_columnconfigure((0, 1), weight=1)

# Second group box for main taper to represent the 9 measurable cookies
taper_group = LabelFrame(processing_tab, text="Main Taper", padx=10, pady=10)
taper_group.pack(side="top", fill="x", padx=20, pady=10)

main_taper_group = []
for i in range(5, 14):
    row = (i-1) // 2
    col = (i-1) % 2
    tk.Label(taper_group, text=f"Cookie {i}:", font=("Arial", 12)).grid(row=row, column=col*2, sticky="e", padx=(5, 2), pady=5)
    entry = tk.Entry(taper_group, bg="lightgrey", font=("Arial", 12))
    entry.grid(row=row, column=col*2+1, sticky="ew", padx=(2, 5), pady=5)
    main_taper_group.append(entry)

# Configure columns to have uniform weight
taper_group.grid_columnconfigure((0, 1), weight=1)

dropdown_label = tk.Label(database_tab, text="Select a tree:", font=("Helvetica", 12))
dropdown_label.pack(pady=10)

tree_name_var = tk.StringVar()
dropdown = ttk.Combobox(database_tab, textvariable=tree_name_var)
dropdown.pack(pady=10)
dropdown.bind('<Button-1>', update_tree_dropdown)  # Refresh dropdown on click

# visualize_button = tk.Button(tab2, text="Visualize Selected Tree", command=visualize_selected_tree, font=("Helvetica", 12))
# visualize_button.pack(pady=5)

delete_button = tk.Button(database_tab, text="Delete Selected Tree", command=delete_selected_tree, font=("Helvetica", 12))
delete_button.pack(pady=5)

download_raw_scan_button = tk.Button(database_tab, text="Download Raw Scan", command=lambda: download_scan_action("raw"), font=("Helvetica", 12))
download_cleaned_scan_button = tk.Button(database_tab, text="Download Cleaned Scan", command=lambda: download_scan_action("cleaned"), font=("Helvetica", 12))
download_preprocessed_scan_button = tk.Button(database_tab, text="Download Preprocessed Scan", command=lambda: download_scan_action("preprocessed"), font=("Helvetica", 12))
download_raw_scan_button.pack(pady=5)
download_cleaned_scan_button.pack(pady=5)
download_preprocessed_scan_button.pack(pady=5)

root.mainloop()