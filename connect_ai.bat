@echo off
setlocal
cd /d "%~dp0"
title MediGuide AI connection setup
if not exist ".venv\Scripts\python.exe" (
    echo Run setup_mediguide.bat first.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" connect_ai.py
if errorlevel 1 (
    pause
    exit /b 1
)
echo Close any previous MediGuide server with Ctrl+C before continuing.
pause
call run_mediguide.bat
