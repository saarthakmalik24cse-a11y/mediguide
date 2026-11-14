@echo off
setlocal
cd /d "%~dp0"
title MediGuide - Free local AI setup
if not exist ".venv\Scripts\python.exe" (
    echo Run setup_mediguide.bat first.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" connect_local_ai.py
pause
