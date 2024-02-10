@echo off
pyinstaller --paths ./pinecone_venv/Lib/site-packages --additional-hooks-dir=hooks --name=Project_Pinecone --onefile frontend/main.py --add-data "./backend;./backend" --hidden-import=open3d --hidden-import=sklearn.ensemble --hidden-import=numpy --icon ./resources/icons/pinecone_icon.ico
pause
