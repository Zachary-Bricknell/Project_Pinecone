import tkinter as tk
from tkinter import filedialog
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

def process_file():
    file_path = file_path_label.cget("text").split("File Path: ")[1]
    destination_directory = os.path.join(os.path.dirname(file_path), "pinecone")
    
    # Ensure the destination directory exists
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)
        
    # Call the backend process function with the original file path and the destination directory
    processed_file_path = process(file_path, destination_directory)

    # You might want to update the UI or notify the user that processing is complete
    print(f"Processed file saved at {processed_file_path}")
    
def visualize_file():
    file_path = file_path_label.cget("text").split("File Path: ")[1]
    visualize(file_path)
    
def process_and_visualize_file():
    file_path = file_path_label.cget("text").split("File Path: ")[1]
    destination_directory = os.path.join(os.path.dirname(file_path), "pinecone")
    process_and_visualize(file_path, destination_directory)
    
# Helper Function for Pyinstaller to find the "resources" folder when packaged
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

root = tk.Tk()
root.title("Pinecone Project")
root.geometry("800x600")

icon_path = resource_path('resources/icons/pinecone_icon.ico')
root.iconbitmap(icon_path)

frame = tk.Frame(root, padx=20, pady=20)
frame.pack(expand=True, fill="both")

file_path_label = tk.Label(frame, text="File Path:", font=("Helvetica", 12))
file_path_label.pack(pady=10)

browse_button = tk.Button(frame, text="Browse", command=browse_file, font=("Helvetica", 12))
browse_button.pack(pady=10)

process_button = tk.Button(frame, text="Process File", command=process_file, font=("Helvetica", 12), state="disabled")
process_button.pack(pady=10)

visualize_button = tk.Button(frame, text="Visualize File", command=visualize_file, font=("Helvetica", 12), state="disabled")
visualize_button.pack(pady=10)

process_and_visualize_button = tk.Button(frame, text="Process and Visualize File", command=process_and_visualize_file, font=("Helvetica", 12), state="disabled")
process_and_visualize_button.pack(pady=10)

root.mainloop()