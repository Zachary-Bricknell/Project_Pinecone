import tkinter as tk
from tkinter import filedialog, LabelFrame
import subprocess
import os
import sys
# For pyinstaller pathing
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.main import process, visualize, process_and_visualize

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("XYZ Files", "*.xyz")])
    if file_path:
        file_path_label.config(text=f"File Path: {file_path}")
        process_button["state"] = "normal"
        visualize_button["state"] = "normal"
        process_and_visualize_button["state"] = "normal"
        
        for entry in dbh_height_group + main_taper_group:
            entry.delete(0, tk.END)

def process_file():
    file_path = file_path_label.cget("text").split("File Path: ")[1]
    destination_directory = os.path.join(os.path.dirname(file_path), "pinecone")

    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    processed_file = process(file_path, destination_directory)
    update_entries(processed_file)
    
def visualize_file():
    file_path = file_path_label.cget("text").split("File Path: ")[1]
    visualize(file_path)
    
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

def update_entries(data):
    """
    Takes in a list of dictionaries representing height and diameter respectively and updates the 
    textbox entries, set to 2 decimal places each.
    """
    for i, entry in enumerate(dbh_height_group + main_taper_group):
        height = data[i]['height']
        diameter = data[i]['diameter']
        entry.delete(0, tk.END) 
        entry.insert(0, "H: {:.2f} D: {:.2f}".format(height, diameter))


root = tk.Tk()
root.title("Pinecone Project")

window_width = 800
window_height = 500
root.geometry(f"{window_width}x{window_height}")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int((screen_width - window_width) / 2)
center_y = int((screen_height - window_height) / 2)
root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

file_path_frame = tk.Frame(root)
file_path_frame.pack(side="top", fill="x")

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

# First group box for DBH entries
dbh_group = LabelFrame(root, text="DBH", padx=10, pady=10)
dbh_group.pack(side="top", fill="x", padx=20, pady=10)

dbh_height_group = []
for i in range(1, 5):
    row = (i-1) // 2
    col = (i-1) % 2
    tk.Label(dbh_group, text=f"Cookie {i}:", font=("Arial", 12)).grid(row=row, column=col*2, sticky="e", padx=5, pady=5)
    entry = tk.Entry(dbh_group, bg="lightgrey", font=("Arial", 12))
    entry.grid(row=row, column=col*2+1, sticky="ew", padx=5, pady=5)
    dbh_height_group.append(entry)

# Second group box for main taper
taper_group = LabelFrame(root, text="Main Taper", padx=10, pady=10)
taper_group.pack(side="top", fill="x", padx=20, pady=10)

main_taper_group = []
for i in range(5, 14):
    row = (i-1) // 2
    col = (i-1) % 2
    tk.Label(taper_group, text=f"Cookie {i}:", font=("Arial", 12)).grid(row=row, column=col*2, sticky="e", padx=5, pady=5)
    entry = tk.Entry(taper_group, bg="lightgrey", font=("Arial", 12))
    entry.grid(row=row, column=col*2+1, sticky="ew", padx=5, pady=5)
    main_taper_group.append(entry)

root.mainloop()