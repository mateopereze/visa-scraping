@echo off
cd /d %~dp0

echo Activating virtual environment...
call .venv\Scripts\activate

echo Virtual environment activated. Running script...
python src\ejecution.py

pause