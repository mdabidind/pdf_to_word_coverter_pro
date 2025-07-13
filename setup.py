#!/usr/bin/env python3

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="pdf-to-word-ocr",
    version="1.0.0",
    description="Convert PDF files to editable Word documents using OCR",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="PDF to Word OCR Converter",
    author_email="example@example.com",
    url="https://github.com/yourusername/pdf-to-word-ocr",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pytesseract>=0.3.8",
        "pdf2image>=1.16.0",
        "python-docx>=0.8.11",
        "Pillow>=8.3.2",
    ],
    entry_points={
        "console_scripts": [
            "pdf-to-word=pdf_to_word_ocr:main",
            "pdf-to-word-batch=batch_convert:main",
            "pdf-to-word-server=web_server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    keywords="pdf, word, ocr, converter, document, tesseract",
)