import tkinter as tk
from tkinter import filedialog, LabelFrame
import subprocess
import os
import sys
import threading

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.main import process, visualize_point_cloud, process_and_visualize

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
        
        for entry in dbh_height_group + main_taper_group:
            entry.delete(0, tk.END)

@wait_while_processing
def process_file():
    file_path = file_path_label.cget("text").split("File Path: ")[1]
    destination_directory = os.path.join(os.path.dirname(file_path), "pinecone")

    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    processed_file, _ = process(file_path, destination_directory)
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

def update_entries(cookie_data):
    """
    Description:
    Takes a list of dictionaires depicting the height ('height' key) and diameter ('diameter' value) of 
    each cookie.
    
    Parameters:
    Data(List): A list of dictionaries
    """
    for i, entry in enumerate(dbh_height_group + main_taper_group):
        height = cookie_data[i]['height']
        diameter = cookie_data[i]['diameter']
        entry.delete(0, tk.END) # Clears any previous entries
        entry.insert(0, "H: {:.2f} D: {:.2f}".format(height, diameter))

def update_status(message):
    status_label.config(text=message)
    
## Tkinter window

root = tk.Tk()
root.title("Pinecone Project")

window_width = 650
window_height = 700
root.geometry(f"{window_width}x{window_height}")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int((screen_width - window_width) / 2)
center_y = int((screen_height - window_height) / 2)
root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

file_path_frame = tk.Frame(root)
file_path_frame.pack(side="top", fill="x")

status_label = tk.Label(file_path_frame, text="Ready", font=("Arial", 12))
status_label.pack(side="top", fill="x", pady=10)

file_path_label = tk.Label(file_path_frame, text="File Path:", font=("Arial", 12))
file_path_label.pack(side="top", fill="x", pady=10)

button_frame = tk.Frame(root)
button_frame.pack(side="top", pady=20)

browse_button = tk.Button(button_frame, text="Browse", command=browse_file, font=("Arial", 12))
browse_button.pack(side="left", padx=10)

process_button = tk.Button(button_frame, text="Process File", command=process_file, font=("Arial", 12), state="disabled")
process_button.pack(side="left", padx=10)

visualize_button = tk.Button(button_frame, text="Visualize File", command=visualize_file, font=("Arial", 12), state="disabled")
visualize_button.pack(side="left", padx=10)

process_and_visualize_button = tk.Button(button_frame, text="Process and Visualize File", command=process_and_visualize_file, font=("Arial", 12), state="disabled")
process_and_visualize_button.pack(side="left", padx=10)

# Group box for tree overview
tree_information_group = tk.LabelFrame(root, text="Tree Information", padx=10, pady=10)
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
dbh_group = LabelFrame(root, text="DBH", padx=10, pady=10)
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
taper_group = LabelFrame(root, text="Main Taper", padx=10, pady=10)
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

root.mainloop()