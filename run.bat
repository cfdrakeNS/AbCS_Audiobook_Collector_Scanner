@echo off
REM Quick run script for AbCS

REM Activate virtual environment if it exists
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

REM Run the application
python src\main.py
