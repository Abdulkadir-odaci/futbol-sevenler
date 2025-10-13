@echo off
echo ========================================
echo   Futbol Sevenler Attendance Tracker
echo   Setup Script
echo ========================================
echo.

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)
echo ✓ Python is installed

echo.
echo [2/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed

echo.
echo [3/4] Verifying installation...
python -c "import streamlit; print('✓ Streamlit installed successfully')"
python -c "import pandas; print('✓ Pandas installed successfully')"
python -c "import plotly; print('✓ Plotly installed successfully')"

echo.
echo [4/4] Setup complete!
echo.
echo ========================================
echo Ready to run the application!
echo ========================================
echo.
echo To start the app, run:
echo   streamlit run app.py
echo.
echo Or double-click on 'run_app.bat'
echo.
pause