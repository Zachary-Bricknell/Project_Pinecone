import tkinter as tk
from tkinter import filedialog
import subprocess
import os


def browse_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("XYZ Files", "*.xyz")],
    )

    if file_path:
        file_path_label.config(text=f"File Path: {file_path}")
        process_button["state"] = "normal"
        visualize_button["state"] = "normal"
        process_and_visualize_button["state"] = "normal"
        
def call_backend(file_path, command):
    # Get the absolute path to the backend script
    backend_script = os.path.abspath("backend\\main.py")

    # Call the backend script with the selected file path and command
    subprocess.run(["python", backend_script, file_path, command])

#new method for processing and visualizing same time
def call_backend_for_process_visualize(file_path, command1, command2):
    backend_script = os.path.abspath("backend\\main.py")

    # Call the backend script with the selected file path and command
    subprocess.run(["python", backend_script, file_path] + command1.split() + command2.split())

def process_file():
    # Call the backend with a process command
    file_path = file_path_label.cget("text")[11:]  # Extract file path from label text
    call_backend(file_path, "--process")

def visualize_file():
    # Call the backend with a visualize command
    file_path = file_path_label.cget("text")[11:]  # Extract file path from label text
    call_backend(file_path, "--visualize")
    
def processadnVisualize_file():
    file_path = file_path_label.cget("text")[11:]
    call_backend_for_process_visualize(file_path, "--process","--visualize")
    

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

process_and_visualize_button = tk.Button(frame, text="Process and Visualize File", command=processadnVisualize_file, font=("Helvetica", 12), state="disabled")
process_and_visualize_button.pack(pady=10)

root.mainloop()