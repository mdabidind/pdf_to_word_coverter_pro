#!/usr/bin/env python3

"""
Basic tests for PDF to Word OCR Converter
"""

import os
import sys
import unittest
import tempfile
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the modules to test
try:
    from pdf_to_word_ocr import setup_tesseract, convert_pdf_to_word
    from batch_convert import batch_convert
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

class TestPDFToWordOCR(unittest.TestCase):
    """Test cases for PDF to Word OCR Converter"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        
        # Skip tests if Tesseract is not installed
        try:
            setup_tesseract()
        except Exception as e:
            self.skipTest(f"Tesseract not properly configured: {e}")
    
    def tearDown(self):
        """Clean up test environment"""
        self.temp_dir.cleanup()
    
    def create_test_pdf(self):
        """Create a test PDF file"""
        try:
            # Try to import reportlab for PDF creation
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            # Create a test PDF file
            pdf_path = self.test_dir / "test.pdf"
            
            # Create a simple PDF with some text
            c = canvas.Canvas(str(pdf_path), pagesize=letter)
            c.setFont("Helvetica", 12)
            c.drawString(100, 750, "PDF to Word OCR Converter Test Document")
            c.drawString(100, 730, "This is a test PDF file created for testing the converter.")
            c.drawString(100, 710, "If you can read this text in the converted Word document, the test is successful.")
            c.save()
            
            return pdf_path
        except ImportError:
            self.skipTest("ReportLab package is not installed. Cannot create test PDF.")
            return None
    
    def test_convert_pdf_to_word(self):
        """Test converting a PDF to Word"""
        # Create test PDF
        pdf_path = self.create_test_pdf()
        if pdf_path is None:
            return
        
        # Set output path
        output_path = self.test_dir / "test.docx"
        
        # Convert PDF to Word
        result = convert_pdf_to_word(str(pdf_path), str(output_path))
        
        # Check if conversion was successful
        self.assertTrue(result, "Conversion failed")
        self.assertTrue(output_path.exists(), "Output file does not exist")
        self.assertTrue(output_path.stat().st_size > 0, "Output file is empty")
    
    def test_batch_convert(self):
        """Test batch converting PDFs to Word"""
        # Create test PDF
        pdf_path = self.create_test_pdf()
        if pdf_path is None:
            return
        
        # Create output directory
        output_dir = self.test_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Batch convert
        result = batch_convert(
            input_dir=str(self.test_dir),
            output_dir=str(output_dir),
            lang="eng",
            dpi=300,
            max_workers=1
        )
        
        # Check if conversion was successful
        self.assertTrue(result, "Batch conversion failed")
        
        # Check if output file exists
        output_path = output_dir / "test.docx"
        self.assertTrue(output_path.exists(), "Output file does not exist")
        self.assertTrue(output_path.stat().st_size > 0, "Output file is empty")

if __name__ == "__main__":
    unittest.main()