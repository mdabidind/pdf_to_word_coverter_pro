#!/usr/bin/env python3

"""
Test script for PDF to Word OCR Converter

This script tests the functionality of the PDF to Word OCR converter by:
1. Checking if all required dependencies are installed
2. Creating a test PDF file
3. Converting the test PDF to a Word document
4. Verifying the conversion was successful
"""

import os
import sys
import tempfile
import platform
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_converter')

def check_python_version():
    """Check if Python version is 3.6 or higher"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        logger.error(f"Python 3.6 or higher is required. Found {sys.version}")
        return False
    
    logger.info(f"Python version: {sys.version}")
    return True

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    try:
        # Try to import pytesseract
        import pytesseract
        version = pytesseract.get_tesseract_version()
        logger.info(f"Tesseract version: {version}")
        return True
    except Exception as e:
        logger.error(f"Tesseract check failed: {e}")
        
        # Provide installation instructions based on OS
        system = platform.system()
        if system == 'Windows':
            logger.info("On Windows, install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
        elif system == 'Darwin':  # macOS
            logger.info("On macOS, install Tesseract using: brew install tesseract")
        elif system == 'Linux':
            logger.info("On Linux, install Tesseract using: sudo apt-get install tesseract-ocr")
        
        return False

def check_poppler():
    """Check if Poppler utilities are installed"""
    try:
        # Try to import pdf2image which requires poppler
        from pdf2image import pdfinfo_from_path
        logger.info("Poppler utilities check passed")
        return True
    except Exception as e:
        logger.error(f"Poppler utilities check failed: {e}")
        
        # Provide installation instructions based on OS
        system = platform.system()
        if system == 'Windows':
            logger.info("On Windows, download Poppler from: https://github.com/oschwartz10612/poppler-windows/releases")
        elif system == 'Darwin':  # macOS
            logger.info("On macOS, install Poppler using: brew install poppler")
        elif system == 'Linux':
            logger.info("On Linux, install Poppler using: sudo apt-get install poppler-utils")
        
        return False

def check_dependencies():
    """Check if all required Python packages are installed"""
    required_packages = ['pytesseract', 'pdf2image', 'python-docx', 'Pillow']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing Python packages: {', '.join(missing_packages)}")
        logger.info("Install required packages using: pip install -r requirements.txt")
        return False
    
    logger.info("All required Python packages are installed")
    return True

def create_test_pdf():
    """Create a test PDF file"""
    try:
        # Try to import reportlab for PDF creation
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            pdf_path = temp_file.name
        
        # Create a simple PDF with some text
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, "PDF to Word OCR Converter Test Document")
        c.drawString(100, 730, "This is a test PDF file created for testing the converter.")
        c.drawString(100, 710, "If you can read this text in the converted Word document, the test is successful.")
        c.save()
        
        logger.info(f"Created test PDF file: {pdf_path}")
        return pdf_path
    except ImportError:
        logger.error("ReportLab package is not installed. Cannot create test PDF.")
        logger.info("Install ReportLab using: pip install reportlab")
        return None
    except Exception as e:
        logger.error(f"Error creating test PDF: {e}")
        return None

def test_conversion():
    """Test the PDF to Word conversion"""
    # Check Python version
    if not check_python_version():
        return False
    
    # Check Tesseract
    if not check_tesseract():
        return False
    
    # Check Poppler
    if not check_poppler():
        return False
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Create test PDF
    pdf_path = create_test_pdf()
    if not pdf_path:
        return False
    
    # Import the converter module
    try:
        from pdf_to_word_ocr import convert_pdf_to_word
    except ImportError:
        logger.error("Could not import pdf_to_word_ocr.py. Make sure it's in the same directory.")
        return False
    
    # Set output path
    output_path = pdf_path.replace('.pdf', '.docx')
    
    # Convert PDF to Word
    logger.info("Converting test PDF to Word...")
    success = convert_pdf_to_word(pdf_path, output_path)
    
    # Check if conversion was successful
    if success and os.path.exists(output_path):
        logger.info(f"Conversion successful! Word document created: {output_path}")
        
        # Clean up test files
        try:
            os.remove(pdf_path)
            os.remove(output_path)
            logger.info("Test files cleaned up")
        except:
            pass
        
        return True
    else:
        logger.error("Conversion failed!")
        return False

def main():
    logger.info("Starting PDF to Word OCR Converter test")
    
    if test_conversion():
        logger.info("All tests passed! The converter is working correctly.")
        return 0
    else:
        logger.error("Tests failed! Please check the error messages above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())