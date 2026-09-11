@echo off
title DepthWizard - Single-View Height Estimation & 3D Flythrough (SIH26175)
color 0B

echo =========================================================================
echo   DEPTHWIZARD - SMART INDIA HACKATHON 2026 (PS ID: SIH26175)
echo   Theme: Disaster Management
echo   Single-View Height Estimation & Interactive 3D Flythrough
echo =========================================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH! Please install Python 3.10+.
    pause
    exit /b 1
)

echo [2/3] Checking dependencies...
python -m pip install -q fastapi uvicorn python-multipart requests pillow numpy scipy matplotlib tifffile

echo [3/3] Launching DepthWizard Engine on http://127.0.0.1:8000 ...
start "" http://127.0.0.1:8000

echo.
echo =========================================================================
echo   Server is active! Press Ctrl+C in this terminal window to stop.
echo =========================================================================
echo.

python backend/app.py

pause
