<h1 align="center">
  :evergreen_tree:Project Pinecone:evergreen_tree:
</h1>

## Purpose
Project Pinecone leverages advanced LiDAR technology to transform scanned trees into precise tree taper models, aiming to reduce or eliminate the need for destructive sampling in forestry. By collaborating with the Ministry of Natural Resources and Forestry (MNRF), we provide an innovative, non-invasive approach to obtaining essential tree metrics such as Diameter, Age, and Height, facilitating sustainable forestry management and conservation efforts.

## Features
- **LiDAR Data Processing**: Employ cutting-edge algorithms to clean and process raw LiDAR scans of Red Pine Trees.
- **Tree Taper Model Generation**: Transform processed LiDAR data into detailed tree taper models for accurate geometric analysis.
- **On-Demand Tree Information**: Instantly access critical statistics including Diameter, Age, Height, and more from the taper models.

## Use Cases
*Accepts only a single .xyz file at a time for processing, saves the file in a directory called ./pinecone where root is the location of the selected input. Currently only support for Windows.*
- **Cleaning Data**: Cleans the input point cloud to produce a single tree taper of the largest tree in the scan. The scan is expected to be a raw, segmented Red Pine tree to be able to extract a taper from. Multiple trees are not supported.
- **Visualize Data**: Visualize any .xyz point cloud using open3d. This will open a new window with displays the pointcloud visually to inspect. If processed, the acquired data will be visualized as well.
- **Metric acquisition**: Obtains valuable metrics from the tree taper automatically, which is saved without requiring visualization. This is saved to a readable JSON file.
- **Compare Data**: When processing & visualizing, compares the input with the output in the same window, similar to the Visualize option, except processing the raw point cloud first. If already processed, it will skip to visualize. 

## Installation
*Currently only support for Windows*
1. Clone the repository: ```git clone https://github.com/Zachary-Bricknell/Project_Pinecone.git```
2. Navigate to project directory: ```cd project_pinecone```
3. Create a virtual environment: ```python -m venv pinecone_venv```
4. Activate the Venv:  windows: ``` pinecone_venv\Scripts\activate``` Linux/MacOS ```source pinecone_venv/bin/activate```
5. Install the dependencies: ```pip install -r requirements.txt```

## Packaging
*Currently only for Windows*
1. Get Pyinstaller: ```pip install pyinstaller```
2. Run the inclided pinecone_installer.bat file, or use the code at the bottom of the page directly
4. Go to the newly created ./dist folder, inside will have project.pinecone.exe


## Usage
To use Project Pinecone through the command line only, ensure you are in the project's root directory with the virtual environment activated.

- To visualize a LiDAR scan: python ./backend/main.py --visualize <path_to_processed_scan>
- To process a LiDAR scan: python ./backend/main.py --process <path_to_processed_scan>
- To process and then visualize a LiDAR scan: ./backend/main.py --process --visualize <path_to_processed_scan>

To use Project Pinecone through the frontend or packaged executable

(optional) If using the CLI to launch the frontend, do ```python ./frontend/main.py```
1. Select the only available button to select an input file (only .xyz is supported currently)
2. Select one of the buttons to process, visualize, or process and visualize


## Installation Script
```pyinstaller --paths ./pinecone_venv/Lib/site-packages --additional-hooks-dir=hooks --name=Project_Pinecone --onefile frontend/main.py --add-data "./backend;./backend" --hidden-import=open3d --hidden-import=sklearn.ensemble --hidden-import=numpy --icon ./resources/icons/pinecone_icon.ico```

- pyinstaller: This is the command to invoke PyInstaller itself.
- --paths ./pinecone_venv/Lib/site-packages: This option adds specified directories to the search path for Python modules. It is used here to include the site-packages directory of the virtual environment (pinecone_venv), where all your project's dependencies are installed
- --additional-hooks-dir=hooks: PyInstaller uses "hooks" to include non-Python files and hidden imports that are not automatically detected. This option tells PyInstaller to look in the specified hooks directory for any additional hooks you've defined. Currently none but included for best practice. 
- --name=Project_Pinecone: Sets the name of the output executable. 
- --onefile: Creates a single executable file. 
- frontend/main.py: The path to the Python script that serves as the frontend. 
- --hidden-import=open3d, --hidden-import=sklearn.ensemble, --hidden-import=numpy: These options tell PyInstaller to explicitly include these Python packages in the bundle, if its not already found.
- --icon ./resources/icons/pinecone_icon.ico: Sets the icon for the executable


## Project Members
- **[Zachary Bricknell](https://github.com/Zachary-Bricknell)**: PM/SWE
- **[Luka](https://github.com/lukanikolaisvili)**: SWE
- **[Kelly](https://github.com/kelly)**: SWE
- **[Mohammed](https://github.com/Mohammed)**: SWE
- **[Frederick](https://github.com/Frederick)**: SWE


## Resources
- [Open3d](https://www.open3d.org/docs/release/introduction.html): Most preprocessing functions and visualizatoin
- [PyInstaller](https://pyinstaller.org/en/stable/): Python packaging documentation
- [Numpy](https://numpy.org/doc/stable/search.html?q=cluster): Preprocessing functionality and point data maniupulation
- [Scikit-learn: Isolation Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html): Preprocessing technique for Isolation Forest
- [Scikit-learn: Dbscan](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html): Preprocessing technique for DBSCAN
