FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-fra \
    tesseract-ocr-deu \
    tesseract-ocr-spa \
    tesseract-ocr-ita \
    tesseract-ocr-por \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY *.py .
COPY *.html .
COPY *.css .
COPY *.js .

# Create directories for uploads and downloads
RUN mkdir -p /app/uploads /app/downloads

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "web_server.py", "--host", "0.0.0.0", "--port", "8080"]