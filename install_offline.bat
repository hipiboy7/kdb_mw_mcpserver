@echo off
:: ============================================================
:: install_offline.bat
:: Offline package installer (no internet required)
::
:: Usage:
::   1. Double-click this file, OR
::   2. Run in cmd: install_offline.bat
:: ============================================================

echo.
echo ====================================================
echo  mcp_kdb_mw Offline Package Installer
echo ====================================================
echo.

:: Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed.
    echo Please install Python 3.10 or higher first.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python version:
python --version
echo.

:: Check wheels folder
if not exist "wheels\" (
    echo [ERROR] wheels folder not found.
    echo The wheels folder must exist in the project directory.
    pause
    exit /b 1
)

echo [START] Installing packages from wheels folder...
echo.

:: --no-index   : do not use PyPI (internet)
:: --find-links : find packages in this folder
:: -r           : install packages listed in requirements.txt
pip install --no-index --find-links=./wheels -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Installation failed.
    echo Python version may not match. Recommended: Python 3.12
    pause
    exit /b 1
)

echo.
echo ====================================================
echo  Installation complete!
echo  Next: create .env file and run main.py
echo ====================================================
echo.
pause
