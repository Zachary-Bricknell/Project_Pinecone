<h1 align="center">
  :evergreen_tree:Project Pinecone:evergreen_tree:
</h1>

## Purpose
Project Pinecone aims to utilize modern noise reduction techniques in LiDAR scans to convert scanned trees into tree taper models. Traditionally, obtaining tree measurements like Diameter, Age, and Height required destructive sampling. Our project seeks to reduce or eliminate this need, providing on-demand, up-to-date tree information. We're collaborating with the MNRF to leverage this technology.

## Features
- **LiDAR Data Processing**: Process and clean raw LiDAR scans of Red Pine Trees.
- **Tree Taper Model Generation**: Convert cleaned LiDAR scans into accurate tree taper models.
- **On-Demand Tree Information**: Access Diameter, Age, Height, and other vital statistics from the generated taper models.

## Installation
Project Pinecone is a Python-based application. The base requirement is python and pip To set up the project:

1. Clone the repository: ```git clone https://github.com/Zachary-Bricknell/Project_Pinecone.git\```
2. Navigate to project directory: ```cd project_pinecone```
3. *optional:* create a virtual enviornment: ```python -m venv pinecone_venv```
4.  Activate the Venv(if created on step 3):  windows: ``` pinecone_venv\Scripts\activate``` Linux/MacOS ```source pinecone_venv/bin/activate```
5.  Install the dependencies: ```pip install requirements.txt```

Open3d may require special instructions based on python/os version. visit http://www.open3d.org/ for details.

## Usage
To use Project Pinecone, ensure you are in the project's root directory with the virtual environment activated.

- To visualize a LiDAR scan: python ./backend/main.py --visualize <path_to_processed_scan>
- To process a LiDAR scan: python ./backend/main.py --process <path_to_processed_scan>
- To process and then visualize a LiDAR scan: ./backend/main.py --process --visualize <path_to_processed_scan>

## Project Members

- **[Zachary Bricknell](https://github.com/Zachary-Bricknell)**: PM/SWE
- **[Luka](https://github.com/lukanikolaisvili)**: SWE
- **[Kelly](https://github.com/kelly)**: SWE
- **[Mohammed](https://github.com/Mohammed)**: SWE
- **[Frederick](https://github.com/Frederick)**: SWE


