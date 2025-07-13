#!/usr/bin/env python3

"""
Batch PDF to Word OCR Converter

This script provides batch conversion functionality for converting multiple PDF files
to Word documents using OCR (Optical Character Recognition).

Usage:
    python batch_convert.py input_path [-o output_dir] [-l lang] [-d dpi] [-w workers]

Options:
    -o, --output-dir    Output directory for Word documents
    -l, --lang          OCR language (default: eng)
    -d, --dpi           DPI for image conversion (default: 300)
    -w, --workers       Maximum number of worker processes
"""

import os
import sys
import argparse
import glob
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('batch_converter')

# Import the converter module
try:
    from pdf_to_word_ocr import convert_pdf_to_word, setup_tesseract
except ImportError:
    logger.error("Could not import pdf_to_word_ocr.py. Make sure it's in the same directory.")
    sys.exit(1)

def process_file(args):
    """Process a single PDF file"""
    pdf_path, output_dir, lang, dpi = args
    pdf_path = Path(pdf_path)
    
    if output_dir:
        output_path = Path(output_dir) / pdf_path.with_suffix('.docx').name
    else:
        output_path = pdf_path.with_suffix('.docx')
    
    logger.info(f"Converting {pdf_path} to {output_path}")
    
    try:
        start_time = time.time()
        success = convert_pdf_to_word(pdf_path, output_path, lang, dpi)
        elapsed_time = time.time() - start_time
        
        if success:
            logger.info(f"Successfully converted {pdf_path} in {elapsed_time:.2f} seconds")
        else:
            logger.error(f"Failed to convert {pdf_path}")
            
        return pdf_path, success, elapsed_time
    except Exception as e:
        logger.error(f"Error processing {pdf_path}: {e}")
        return pdf_path, False, 0

def batch_convert(input_path, output_dir=None, lang='eng', dpi=300, max_workers=None):
    """Convert multiple PDF files to Word documents"""
    # Ensure output directory exists if specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Get list of PDF files to process
    if os.path.isdir(input_path):
        pdf_files = glob.glob(os.path.join(input_path, '**', '*.pdf'), recursive=True)
    elif os.path.isfile(input_path) and input_path.lower().endswith('.pdf'):
        pdf_files = [input_path]
    else:
        # Try to use glob pattern
        pdf_files = glob.glob(input_path, recursive=True)
    
    if not pdf_files:
        logger.error(f"No PDF files found at {input_path}")
        return False
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Check if Tesseract is configured
    if not setup_tesseract():
        logger.warning("Tesseract OCR is not properly configured. Conversions may fail.")
    
    # Prepare arguments for processing
    process_args = [(pdf, output_dir, lang, dpi) for pdf in pdf_files]
    
    # Set default max_workers if not specified
    if max_workers is None:
        max_workers = max(1, multiprocessing.cpu_count() - 1)  # Leave one CPU free
    
    # Process files in parallel
    successful = 0
    failed = 0
    total_time = 0
    
    logger.info(f"Starting batch conversion with {max_workers} worker processes")
    start_time = time.time()
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for pdf_path, success, elapsed_time in executor.map(process_file, process_args):
            if success:
                successful += 1
                total_time += elapsed_time
            else:
                failed += 1
    
    total_elapsed = time.time() - start_time
    
    logger.info(f"Batch conversion complete in {total_elapsed:.2f} seconds")
    logger.info(f"Results: {successful} successful, {failed} failed")
    
    if successful > 0:
        avg_time = total_time / successful
        logger.info(f"Average conversion time: {avg_time:.2f} seconds per file")
    
    return successful > 0

def main():
    parser = argparse.ArgumentParser(description='Batch convert PDF files to Word documents using OCR')
    parser.add_argument('input_path', help='Path to PDF file, directory containing PDFs, or glob pattern')
    parser.add_argument('-o', '--output-dir', help='Output directory for Word documents')
    parser.add_argument('-l', '--lang', default='eng', help='OCR language (default: eng)')
    parser.add_argument('-d', '--dpi', type=int, default=300, help='DPI for image conversion (default: 300)')
    parser.add_argument('-w', '--workers', type=int, default=None, help='Maximum number of worker processes')
    args = parser.parse_args()
    
    success = batch_convert(
        args.input_path,
        args.output_dir,
        args.lang,
        args.dpi,
        args.workers
    )
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())