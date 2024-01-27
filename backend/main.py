import tkinter as tk
from tkinter import filedialog
import os
import shutil
from utils.point_cloud_utils import visualize_point_cloud
from point_cloud_processor import process_point_cloud

def browse_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("XYZ Files", "*.xyz")],
    )

    if file_path:
        file_path_label.config(text=f"File Path: {file_path}")
        process_button["state"] = "normal"
        visualize_button["state"] = "normal"
        process_and_visualize_button["state"] = "normal"
        return file_path  # Return the file path when selected

def process_file():
    file_path = file_path_label.cget("text")[11:]  # Extract file path from label text
    process_point_cloud_and_update_ui(file_path)

def visualize_file():
    file_path = file_path_label.cget("text")[11:]  # Extract file path from label text
    visualize_point_cloud(file_path)

def process_and_visualize_file():
    file_path = file_path_label.cget("text")[11:]  # Extract file path from label text
    processed_file_path = process_point_cloud_and_update_ui(file_path)
    visualize_point_cloud(processed_file_path)

def process_point_cloud_and_update_ui(file_path):
    # Process the point cloud
    destination_directory = os.path.join(os.path.dirname(file_path), "pinecone")
    
    # Create the destination directory if it does not exist
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    # Copy the file into the destination directory
    filename = os.path.basename(file_path)
    destination_path = os.path.join(destination_directory, filename)
    shutil.copyfile(file_path, destination_path)

    # Process the point cloud using the path to the copied file, retaining the original data's integrity.
    processed_file_path = process_point_cloud(destination_path, destination_directory)
    print(f"Processed point cloud saved as: {processed_file_path}")
    
    return processed_file_path

root = tk.Tk()
root.title("Pinecone Project")
root.geometry("800x600")

# Create a frame for a cleaner layout
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
