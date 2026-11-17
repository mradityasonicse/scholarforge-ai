@echo off
title ScholarForge AI - University Project Report Generator
color 0b

echo ======================================================================
echo          ScholarForge AI - University Project Report Generator
echo ======================================================================
echo.
echo Checking Python environment...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from python.org and check "Add to PATH".
    pause
    exit /b
)

echo Installing / Verifying required packages...
pip install -r requirements.txt >nul 2>&1

echo.
echo Launching Server and Opening Web Dashboard in your browser...
echo URL: http://127.0.0.1:8000
echo.
python run.py

pause
