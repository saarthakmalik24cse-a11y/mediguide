@echo off
setlocal
cd /d "%~dp0"
title MediGuide setup
if not exist ".venv\Scripts\python.exe" (
    py -3.12 -m venv .venv
    if errorlevel 1 (
        echo Install Python 3.12 first, then run this file again.
        pause
        exit /b 1
    )
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo Package installation failed. Check your internet connection and the error above.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" seed_data.py
if errorlevel 1 (
    echo Sample setup failed. See the error above.
    pause
    exit /b 1
)
call run_mediguide.bat
