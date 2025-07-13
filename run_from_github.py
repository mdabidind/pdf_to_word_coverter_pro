#!/usr/bin/env python3

"""
Run PDF to Word OCR Converter directly from GitHub

This script downloads the latest version of the PDF to Word OCR Converter from GitHub,
sets up the environment, and runs the web server.
"""

import os
import sys
import platform
import subprocess
import tempfile
import shutil
import zipfile
from pathlib import Path
import urllib.request

# GitHub repository information
REPO_OWNER = "yourusername"
REPO_NAME = "pdf-to-word-ocr"
BRANCH = "main"
ZIP_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/archive/refs/heads/{BRANCH}.zip"

# Determine the installation directory
HOME_DIR = str(Path.home())
INSTALL_DIR = os.path.join(HOME_DIR, ".pdf-to-word-ocr")

# Determine the system
SYSTEM = platform.system()

def print_step(message):
    """Print a step message with formatting"""
    print(f"\n[*] {message}")

def check_python_version():
    """Check if Python version is 3.6 or higher"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print(f"Error: Python 3.6 or higher is required. Found {sys.version}")
        return False
    return True

def download_repository():
    """Download the repository from GitHub"""
    print_step(f"Downloading PDF to Word OCR Converter from GitHub...")
    
    # Create a temporary directory for the download
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "repo.zip")
    
    try:
        # Download the ZIP file
        print(f"Downloading from {ZIP_URL}...")
        urllib.request.urlretrieve(ZIP_URL, zip_path)
        
        # Extract the ZIP file
        print("Extracting files...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find the extracted directory
        extracted_dir = None
        for item in os.listdir(temp_dir):
            if item.startswith(f"{REPO_NAME}-"):
                extracted_dir = os.path.join(temp_dir, item)
                break
        
        if not extracted_dir:
            print("Error: Could not find extracted repository directory")
            return None
        
        # Create the installation directory if it doesn't exist
        if os.path.exists(INSTALL_DIR):
            print(f"Removing existing installation at {INSTALL_DIR}...")
            shutil.rmtree(INSTALL_DIR)
        
        print(f"Installing to {INSTALL_DIR}...")
        shutil.copytree(extracted_dir, INSTALL_DIR)
        
        return INSTALL_DIR
    
    except Exception as e:
        print(f"Error downloading repository: {e}")
        return None
    
    finally:
        # Clean up the temporary directory
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

def setup_virtual_environment(install_dir):
    """Set up a virtual environment and install dependencies"""
    print_step("Setting up virtual environment...")
    
    venv_dir = os.path.join(install_dir, "venv")
    
    try:
        # Create virtual environment
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        
        # Determine the pip and python executables in the virtual environment
        if SYSTEM == "Windows":
            python_exe = os.path.join(venv_dir, "Scripts", "python.exe")
            pip_exe = os.path.join(venv_dir, "Scripts", "pip.exe")
        else:
            python_exe = os.path.join(venv_dir, "bin", "python")
            pip_exe = os.path.join(venv_dir, "bin", "pip")
        
        # Install dependencies
        print("Installing dependencies...")
        requirements_file = os.path.join(install_dir, "requirements.txt")
        subprocess.run([pip_exe, "install", "-r", requirements_file], check=True)
        
        return python_exe
    
    except subprocess.CalledProcessError as e:
        print(f"Error setting up virtual environment: {e}")
        return None

def run_web_server(python_exe, install_dir):
    """Run the web server"""
    print_step("Starting PDF to Word OCR Converter...")
    
    web_server_script = os.path.join(install_dir, "web_server.py")
    
    try:
        # Run the web server
        subprocess.run([python_exe, web_server_script], cwd=install_dir)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error running web server: {e}")

def main():
    """Main function"""
    print("PDF to Word OCR Converter - GitHub Runner")
    print("===========================================\n")
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Download the repository
    install_dir = download_repository()
    if not install_dir:
        return 1
    
    # Setup virtual environment
    python_exe = setup_virtual_environment(install_dir)
    if not python_exe:
        return 1
    
    # Run the web server
    run_web_server(python_exe, install_dir)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())