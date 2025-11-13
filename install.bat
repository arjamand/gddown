@echo off
title gddown Full Auto Installer (No Git)
echo ============================================
echo      GDDOWN - Full Automated Setup
echo ============================================
echo.

:: Check for administrator privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Please run this script as Administrator.
    pause
    exit /b 1
)

:: Step 1: Check if Python is installed
echo Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Downloading and installing Python 3.11...
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe -OutFile python_installer.exe"
    echo Installing Python silently...
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del python_installer.exe
    echo Python installed successfully.
) else (
    echo Python is already installed.
)

:: Step 2: Download the repository ZIP
echo.
echo Downloading gddown repository from GitHub...
powershell -Command "Invoke-WebRequest -Uri https://github.com/arjamand/gddown/archive/refs/heads/main.zip -OutFile gddown.zip"

if not exist gddown.zip (
    echo Failed to download repository. Check your internet connection.
    pause
    exit /b 1
)

:: Step 3: Extract the repository
echo.
echo Extracting files...
powershell -Command "Expand-Archive -Path gddown.zip -DestinationPath . -Force"
del gddown.zip

:: Step 4: Rename extracted folder if necessary
if exist gddown-main (
    ren gddown-main gddown
)

cd gddown

:: Step 5: Install dependencies
echo.
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Step 6: Install Playwright browser
echo.
echo Installing Playwright Chromium browser...
playwright install chromium

:: Step 7: Done
echo.
echo ============================================
echo ✅ Installation complete!
echo Repository: %cd%
echo.
echo You can now run the application using:
echo        python gddown.py [options]
echo        python gddown.py --help  for more information
echo        OR using " run-interactive.bat " for interactive mode
echo ============================================
pause
