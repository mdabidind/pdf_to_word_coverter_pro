#!/usr/bin/env python3

"""
PDF to Word OCR Converter Web Server

This script provides a web interface for the PDF to Word OCR converter.
It allows users to upload PDF files, convert them to Word documents using OCR,
and download the resulting files.

Usage:
    python web_server.py [--port PORT] [--host HOST]

Options:
    --port      Port to run the server on (default: 8080)
    --host      Host to run the server on (default: 0.0.0.0)
"""

import os
import sys
import argparse
import logging
import json
import shutil
import tempfile
import time
import uuid
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import mimetypes
import threading
import atexit
import socket
import webbrowser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('web_server')

# Try to import required libraries
try:
    from werkzeug.utils import secure_filename
except ImportError:
    logger.error("Werkzeug library not found. Please install it: pip install werkzeug")
    sys.exit(1)

# Import the converter module
try:
    from pdf_to_word_ocr import convert_pdf_to_word, setup_tesseract
except ImportError:
    logger.error("Could not import pdf_to_word_ocr.py. Make sure it's in the same directory.")
    sys.exit(1)

# Create temporary directories for uploads and downloads
UPLOAD_DIR = tempfile.mkdtemp(prefix='pdf_ocr_uploads_')
DOWNLOAD_DIR = tempfile.mkdtemp(prefix='pdf_ocr_downloads_')
logger.info(f"Upload directory: {UPLOAD_DIR}")
logger.info(f"Download directory: {DOWNLOAD_DIR}")

# Clean up temporary directories on exit
def cleanup_temp_dirs():
    logger.info("Cleaning up temporary directories")
    shutil.rmtree(UPLOAD_DIR, ignore_errors=True)
    shutil.rmtree(DOWNLOAD_DIR, ignore_errors=True)

atexit.register(cleanup_temp_dirs)

# Set up a dictionary to track conversion tasks
conversion_tasks = {}

class PDFToWordHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the PDF to Word OCR converter web interface"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Serve index.html for root path
        if path == '/' or path == '/index.html':
            self.serve_file('index.html', 'text/html')
            return
        
        # Handle file downloads
        if path.startswith('/download/'):
            file_id = path.split('/')[-1]
            self.handle_download(file_id)
            return
        
        # Handle API status check
        if path == '/api/status':
            self.serve_json({'status': 'ok'})
            return
        
        # Serve static files
        if path.startswith('/static/'):
            file_path = path[8:]  # Remove '/static/' prefix
            self.serve_static_file(file_path)
            return
        
        # Serve other static files from the root directory
        if '.' in path[1:]:  # Has file extension
            self.serve_static_file(path[1:])  # Remove leading slash
            return
        
        # Default: 404 Not Found
        self.send_error(404, "File not found")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Handle API convert endpoint
        if path == '/api/convert':
            self.handle_convert()
            return
        
        # Default: 404 Not Found
        self.send_error(404, "File not found")
    
    def serve_static_file(self, file_path):
        """Serve a static file"""
        # Normalize path and prevent directory traversal
        file_path = os.path.normpath(file_path).lstrip('/')
        if '..' in file_path:
            self.send_error(403, "Forbidden")
            return
        
        # Get the full path to the file
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        
        # Check if file exists
        if not os.path.isfile(full_path):
            self.send_error(404, "File not found")
            return
        
        # Determine content type
        content_type, _ = mimetypes.guess_type(full_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        # Serve the file
        try:
            with open(full_path, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(os.path.getsize(full_path)))
                self.end_headers()
                self.wfile.write(f.read())
        except Exception as e:
            logger.error(f"Error serving file {file_path}: {e}")
            self.send_error(500, "Internal Server Error")
    
    def serve_file(self, file_name, content_type):
        """Serve a file with the specified content type"""
        file_path = os.path.join(os.path.dirname(__file__), file_name)
        
        if not os.path.isfile(file_path):
            self.send_error(404, "File not found")
            return
        
        try:
            with open(file_path, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(os.path.getsize(file_path)))
                self.end_headers()
                self.wfile.write(f.read())
        except Exception as e:
            logger.error(f"Error serving file {file_name}: {e}")
            self.send_error(500, "Internal Server Error")
    
    def handle_download(self, file_id):
        """Handle file download requests"""
        # Check if file exists in download directory
        for file_name in os.listdir(DOWNLOAD_DIR):
            if file_name.startswith(file_id):
                file_path = os.path.join(DOWNLOAD_DIR, file_name)
                
                # Serve the file
                try:
                    with open(file_path, 'rb') as f:
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                        self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(file_name)}"')
                        self.send_header('Content-Length', str(os.path.getsize(file_path)))
                        self.end_headers()
                        self.wfile.write(f.read())
                    return
                except Exception as e:
                    logger.error(f"Error serving download {file_id}: {e}")
                    self.send_error(500, "Internal Server Error")
                    return
        
        # File not found
        self.send_error(404, "File not found")
    
    def serve_json(self, data):
        """Serve JSON response"""
        response = json.dumps(data).encode('utf-8')
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)
    
    def handle_convert(self):
        """Handle PDF to Word conversion requests"""
        # Check content type
        content_type = self.headers.get('Content-Type', '')
        if not content_type.startswith('multipart/form-data'):
            self.serve_json({'error': 'Invalid content type'})
            return
        
        # Get content length
        try:
            content_length = int(self.headers.get('Content-Length', 0))
        except ValueError:
            self.serve_json({'error': 'Invalid content length'})
            return
        
        # Read form data
        form_data = self.rfile.read(content_length)
        
        # Parse multipart form data
        try:
            # Find boundary
            boundary = content_type.split('=')[1].strip()
            boundary = boundary.encode('utf-8')
            
            # Split form data by boundary
            parts = form_data.split(b'--' + boundary)
            
            # Process parts
            pdf_file = None
            pdf_filename = None
            ocr_lang = 'eng'
            dpi = 300
            
            for part in parts:
                # Skip empty parts
                if not part.strip() or part.strip() == b'--':
                    continue
                
                # Split headers and content
                try:
                    headers_raw, content = part.split(b'\r\n\r\n', 1)
                    headers_raw = headers_raw.strip()
                    
                    # Parse headers
                    headers = {}
                    for header in headers_raw.split(b'\r\n'):
                        if b':' in header:
                            name, value = header.split(b':', 1)
                            headers[name.strip().lower()] = value.strip()
                    
                    # Get content disposition
                    if b'content-disposition' in headers:
                        disposition = headers[b'content-disposition'].decode('utf-8')
                        parts_dict = {}
                        for item in disposition.split(';'):
                            item = item.strip()
                            if '=' in item:
                                key, value = item.split('=', 1)
                                parts_dict[key] = value.strip('"')
                        
                        # Check if this is a file
                        if 'filename' in parts_dict:
                            if parts_dict.get('name') == 'pdf_file':
                                pdf_filename = parts_dict['filename']
                                # Remove trailing \r\n
                                if content.endswith(b'\r\n'):
                                    content = content[:-2]
                                pdf_file = content
                        # Check if this is a form field
                        elif 'name' in parts_dict:
                            if parts_dict['name'] == 'ocr_lang':
                                ocr_lang = content.decode('utf-8').strip()
                            elif parts_dict['name'] == 'dpi':
                                try:
                                    dpi = int(content.decode('utf-8').strip())
                                except ValueError:
                                    pass
                except Exception as e:
                    logger.error(f"Error parsing form part: {e}")
                    continue
            
            # Check if PDF file was uploaded
            if pdf_file is None or pdf_filename is None:
                self.serve_json({'error': 'No PDF file uploaded'})
                return
            
            # Validate filename
            pdf_filename = secure_filename(pdf_filename)
            if not pdf_filename.lower().endswith('.pdf'):
                self.serve_json({'error': 'Invalid file type. Only PDF files are supported.'})
                return
            
            # Generate unique ID for this conversion
            file_id = str(uuid.uuid4())
            
            # Save PDF file
            pdf_path = os.path.join(UPLOAD_DIR, f"{file_id}_{pdf_filename}")
            with open(pdf_path, 'wb') as f:
                f.write(pdf_file)
            
            # Set output path
            output_filename = pdf_filename.rsplit('.', 1)[0] + '.docx'
            output_path = os.path.join(DOWNLOAD_DIR, f"{file_id}_{output_filename}")
            
            # Start conversion in a separate thread
            def convert_thread():
                try:
                    conversion_tasks[file_id] = {'status': 'processing', 'progress': 0}
                    success = convert_pdf_to_word(pdf_path, output_path, ocr_lang, dpi)
                    
                    if success:
                        conversion_tasks[file_id] = {
                            'status': 'completed',
                            'progress': 100,
                            'download_url': f'/download/{file_id}_{output_filename}',
                            'filename': output_filename
                        }
                    else:
                        conversion_tasks[file_id] = {'status': 'failed', 'progress': 100, 'error': 'Conversion failed'}
                    
                    # Clean up upload file
                    try:
                        os.remove(pdf_path)
                    except:
                        pass
                except Exception as e:
                    logger.error(f"Error in conversion thread: {e}")
                    conversion_tasks[file_id] = {'status': 'failed', 'progress': 100, 'error': str(e)}
            
            # Start conversion thread
            thread = threading.Thread(target=convert_thread)
            thread.daemon = True
            thread.start()
            
            # Return task ID
            self.serve_json({
                'task_id': file_id,
                'status': 'processing',
                'message': 'Conversion started'
            })
            
        except Exception as e:
            logger.error(f"Error handling conversion request: {e}")
            self.serve_json({'error': f"Server error: {str(e)}"})


def run_server(host='0.0.0.0', port=8080):
    """Run the HTTP server"""
    # Check if port is available
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
    except OSError:
        logger.warning(f"Port {port} is already in use. Trying another port.")
        # Try to find an available port
        for p in range(port + 1, port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind((host, p))
                port = p
                logger.info(f"Using port {port} instead")
                break
            except OSError:
                continue
    
    # Create server
    server = HTTPServer((host, port), PDFToWordHandler)
    server_url = f"http://{'localhost' if host == '0.0.0.0' else host}:{port}"
    
    logger.info(f"Server running at {server_url}")
    logger.info("Press Ctrl+C to stop the server")
    
    # Open browser
    try:
        webbrowser.open(server_url)
    except:
        logger.warning("Could not open browser automatically. Please navigate to the URL manually.")
    
    # Run server
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        server.server_close()
        logger.info("Server closed")


def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run PDF to Word OCR Converter web server')
    parser.add_argument('--port', type=int, default=8080, help='Port to run the server on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to run the server on')
    args = parser.parse_args()
    
    # Check if Tesseract is configured
    if not setup_tesseract():
        logger.warning("Tesseract OCR is not properly configured. Conversions may fail.")
    
    # Run server
    run_server(args.host, args.port)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())