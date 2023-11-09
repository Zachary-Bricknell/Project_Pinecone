<h1 align="center">
  :evergreen_tree:Project Pinecone:evergreen_tree:
</h1>

## Purpose
The purpose of this project is to create a proof of concept that utilizes modern noise reduction techniques in LiDAR scans to convert a scanned tree into a tree taper model.
Originally the only way to obtain various information such as the Diameter, Age, and Height of a tree was through destructive sampling. With this project, we aim to reduce or
eliminate the need for destructive sampling and have on-demand access to up-to-date information at any given time. We are working closely with the MNRF to utilize this technology.

## Features
- **LiDAR Data Processing**: Ability to process and clean raw LiDAR scans of Red Pine Trees.
- **Tree Taper Model Generation**: Convert cleaned LiDAR scans into tree taper models.
- **On-Demand Tree Information**: Retrieve Diameter, Age, Height, and other relevant statistics from the generated taper.

## Installation
Under Construction

## Build Script

- Remove items denoted with square backets 

```bash
@echo off

rem Set the path to your venv
set VENV_PATH=[Path to VENV]

rem Activate the virtual environment.
call "%VENV_PATH%"

rem Run pyinstaller with the activated virtual environment.
pyinstaller --onefile --windowed --icon=.\resources\icons\temp_icon.ico [Path to project_pinecone.py

rem Pause to see if pyinstaller runs successfully.
pause

exit /b

pause

```

## Project Members

- **[Zachary Bricknell](https://github.com/Zachary-Bricknell)**: PM
- **[Luka](https://github.com/luka)**: SWE
- **[Kelly](https://github.com/kelly)**: SWE
- **[Mohammed](https://github.com/Mohammed)**: SWE
- **[Frederick](https://github.com/Frederick)**: SWE


