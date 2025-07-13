@echo off
setlocal enabledelayedexpansion

echo PDF to Word OCR Converter
echo ========================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.6 or higher from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Check Python version
for /f "tokens=2" %%V in ('python --version 2^>^&1') do (
    set pyver=%%V
)
echo Found Python %pyver%

:: Check if Tesseract is installed
pytesseract --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Checking for Tesseract OCR...
    
    if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
        echo Found Tesseract in Program Files
        set "PATH=%PATH%;C:\Program Files\Tesseract-OCR"
    ) else if exist "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe" (
        echo Found Tesseract in Program Files (x86)
        set "PATH=%PATH%;C:\Program Files (x86)\Tesseract-OCR"
    ) else (
        echo Tesseract OCR is not installed or not in PATH.
        echo Please install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki
        echo.
        pause
        exit /b 1
    )
)

echo.
echo Setting up environment...

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Install requirements
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo Starting PDF to Word OCR Converter...
echo.

:: Start the web server
python web_server.py

:: Deactivate virtual environment
call venv\Scripts\deactivate.bat

endlocal