@echo off
setlocal
cd /d "%~dp0"
title MediGuide server - keep this window open

if not exist ".venv\Scripts\python.exe" (
    echo The MediGuide Python environment is missing.
    echo Run the setup steps in README.md first.
    pause
    exit /b 1
)

echo Starting MediGuide. Keep this window open while using the site.
".venv\Scripts\python.exe" check_setup.py
if errorlevel 1 (
    echo Preflight failed. Run setup_mediguide.bat or review the message above.
    pause
    exit /b 1
)
echo Open http://127.0.0.1:8502 in your browser.
echo This updated launcher uses 8502 to avoid the older server on 8501.
echo Press Ctrl+C here to stop the server.
".venv\Scripts\python.exe" -m streamlit run app.py --server.address 127.0.0.1 --server.port 8502 --browser.gatherUsageStats false

echo.
echo MediGuide stopped. If the site does not reload, read any error above.
pause
