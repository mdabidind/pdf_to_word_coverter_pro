# PDF to Word OCR Converter

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Test PDF to Word OCR Converter](https://github.com/yourusername/pdf-to-word-ocr/actions/workflows/test.yml/badge.svg)](https://github.com/yourusername/pdf-to-word-ocr/actions/workflows/test.yml)
[![Docker Build and Publish](https://github.com/yourusername/pdf-to-word-ocr/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/yourusername/pdf-to-word-ocr/actions/workflows/docker-publish.yml)

A powerful tool to convert PDF files to editable Word documents using Optical Character Recognition (OCR) technology. This application extracts text from PDF files, even scanned documents, and creates fully editable Word documents.

## Features

- Convert PDF files to editable Word documents (.docx)
- Support for scanned documents using OCR technology
- Multiple language support for OCR
- Adjustable DPI settings for quality control
- Batch conversion capability for multiple files
- User-friendly web interface
- Command-line interface for automation
- Local processing for privacy and security
- Docker support for easy deployment

## Requirements

### For Docker Installation
- Docker
- Docker Compose (optional)

### For Manual Installation
- Python 3.6 or higher
- Tesseract OCR
- Poppler utilities (for pdf2image)
- Python packages (see requirements.txt)

## Installation

### Install via pip (Simplest)

```bash
pip install pdf-to-word-ocr
```

Then run the converter:

```bash
# Run the web interface
pdf-to-word-server

# Convert a single file
pdf-to-word input.pdf -o output.docx

# Batch convert files
pdf-to-word-batch input_directory -o output_directory
```

### Run Directly from GitHub (No Installation)

#### Option 1: One-line Python Script (Recommended)

Run this single command in your terminal or command prompt:

```bash
python -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/yourusername/pdf-to-word-ocr/main/run_from_github.py').read().decode())"  
```

This will:
- Download the latest version from GitHub
- Install it in your home directory
- Set up a virtual environment
- Install all dependencies
- Start the web server

#### Option 2: Manual Download

1. Download the repository directly from GitHub:
   ```bash
   # Using git
   git clone https://github.com/yourusername/pdf-to-word-ocr.git
   cd pdf-to-word-ocr
   
   # Or download ZIP file
   # https://github.com/yourusername/pdf-to-word-ocr/archive/refs/heads/main.zip
   ```

2. Run the appropriate script for your operating system:
   - **Windows**: Double-click `run_converter.bat` or run it from Command Prompt
   - **Linux/macOS**: 
     ```bash
     chmod +x run_converter.sh
     ./run_converter.sh
     ```

3. The script will automatically:
   - Check for required dependencies
   - Set up a virtual environment
   - Install required Python packages
   - Start the web server
   - Open the web interface in your browser

### Using Docker (Recommended for Production)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pdf-to-word-ocr.git
   cd pdf-to-word-ocr
   ```

2. Build and run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. Access the web interface at http://localhost:8080

### Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pdf-to-word-ocr.git
   cd pdf-to-word-ocr
   ```

2. Install Tesseract OCR:
   - **Windows**: Download and install from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

3. Install Poppler utilities:
   - **Windows**: Download from [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases)
   - **macOS**: `brew install poppler`
   - **Linux**: `sudo apt-get install poppler-utils`

4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the web server:
   ```bash
   python web_server.py
   ```

6. Access the web interface at http://localhost:8080

## Usage

### Web Interface

1. Open your web browser and navigate to http://localhost:8080
2. Drag and drop a PDF file or click to browse and select a file
3. Choose OCR language and DPI settings
4. Click "Convert to Word"
5. Download the converted Word document when processing is complete

### Command Line

#### Single File Conversion

```bash
python pdf_to_word_ocr.py input.pdf -o output.docx -l eng -d 300
```

Options:
- `-o, --output`: Output Word document path (default: same as input with .docx extension)
- `-l, --lang`: OCR language (default: eng)
- `-d, --dpi`: DPI for image conversion (default: 300)

#### Batch Conversion

```bash
python batch_convert.py input_directory -o output_directory -l eng -d 300 -w 4
```

Options:
- `-o, --output-dir`: Output directory for Word documents
- `-l, --lang`: OCR language (default: eng)
- `-d, --dpi`: DPI for image conversion (default: 300)
- `-w, --workers`: Maximum number of worker processes

## Supported Languages

The converter supports all languages that Tesseract OCR supports, including:

- English (eng)
- French (fra)
- German (deu)
- Spanish (spa)
- Italian (ita)
- Portuguese (por)
- Russian (rus)
- Chinese Simplified (chi_sim)
- Chinese Traditional (chi_tra)
- Japanese (jpn)
- Korean (kor)
- Arabic (ara)
- And many more

To use additional languages, make sure to install the corresponding Tesseract language data packages.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [pdf2image](https://github.com/Belval/pdf2image)
- [python-docx](https://github.com/python-openxml/python-docx)
- [pytesseract](https://github.com/madmaze/pytesseract)