#!/bin/bash

echo "PDF to Word OCR Converter"
echo "========================"
echo 

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed."
    echo "Please install Python 3.6 or higher."
    echo "On Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
    echo "On macOS: brew install python3"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d" " -f2)
echo "Found Python $PYTHON_VERSION"

# Check if Tesseract OCR is installed
if ! command -v tesseract &> /dev/null; then
    echo "Tesseract OCR is not installed."
    echo "Please install Tesseract OCR:"
    echo "On Ubuntu/Debian: sudo apt-get install tesseract-ocr"
    echo "On macOS: brew install tesseract"
    exit 1
fi

TESSERACT_VERSION=$(tesseract --version 2>&1 | head -n 1 | cut -d" " -f2)
echo "Found Tesseract OCR $TESSERACT_VERSION"

# Check if Poppler is installed
if ! command -v pdftoppm &> /dev/null; then
    echo "Poppler utilities are not installed."
    echo "Please install Poppler utilities:"
    echo "On Ubuntu/Debian: sudo apt-get install poppler-utils"
    echo "On macOS: brew install poppler"
    exit 1
fi

echo "Found Poppler utilities"

echo 
echo "Setting up environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies."
    exit 1
fi

echo 
echo "Starting PDF to Word OCR Converter..."
echo 

# Start the web server
python web_server.py

# Deactivate virtual environment
deactivate