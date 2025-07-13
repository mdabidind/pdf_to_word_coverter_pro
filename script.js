document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const removeFile = document.getElementById('removeFile');
    const optionsContainer = document.getElementById('optionsContainer');
    const actionButtons = document.getElementById('actionButtons');
    const convertBtn = document.getElementById('convertBtn');
    const statusContainer = document.getElementById('statusContainer');
    const progressBar = document.getElementById('progressBar');
    const statusText = document.getElementById('statusText');
    const resultContainer = document.getElementById('resultContainer');
    const downloadLink = document.getElementById('downloadLink');
    const errorModal = document.getElementById('errorModal');
    const errorMessage = document.getElementById('errorMessage');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const closeModalX = document.querySelector('.close-modal');
    
    // Selected file
    let selectedFile = null;
    
    // Drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        uploadArea.classList.add('highlight');
    }
    
    function unhighlight() {
        uploadArea.classList.remove('highlight');
    }
    
    // Handle file drop
    uploadArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            handleFiles(files);
        }
    }
    
    // Handle file input change
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            handleFiles(this.files);
        }
    });
    
    // Click on upload area to trigger file input
    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });
    
    // Handle files
    function handleFiles(files) {
        const file = files[0];
        
        // Check if file is a PDF
        if (file.type !== 'application/pdf') {
            showError('Please select a PDF file.');
            return;
        }
        
        // Store selected file
        selectedFile = file;
        
        // Display file info
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        
        // Show file info and options
        fileInfo.style.display = 'block';
        optionsContainer.style.display = 'block';
        actionButtons.style.display = 'flex';
        uploadArea.style.display = 'none';
        
        // Enable convert button
        convertBtn.disabled = false;
    }
    
    // Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Remove file
    removeFile.addEventListener('click', function() {
        resetForm();
    });
    
    // Reset form
    function resetForm() {
        selectedFile = null;
        fileInput.value = '';
        fileInfo.style.display = 'none';
        optionsContainer.style.display = 'none';
        actionButtons.style.display = 'none';
        uploadArea.style.display = 'block';
        statusContainer.style.display = 'none';
        resultContainer.style.display = 'none';
        convertBtn.disabled = true;
    }
    
    // Convert button click
    convertBtn.addEventListener('click', function() {
        if (!selectedFile) {
            showError('Please select a PDF file.');
            return;
        }
        
        // Show status container
        fileInfo.style.display = 'none';
        optionsContainer.style.display = 'none';
        actionButtons.style.display = 'none';
        statusContainer.style.display = 'block';
        
        // Get options
        const ocrLang = document.getElementById('ocrLang').value;
        const dpi = document.getElementById('dpi').value;
        
        // Create form data
        const formData = new FormData();
        formData.append('pdf_file', selectedFile);
        formData.append('ocr_lang', ocrLang);
        formData.append('dpi', dpi);
        
        // Send request
        fetch('/api/convert', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
                resetForm();
                return;
            }
            
            // Start progress simulation
            simulateProgress(data.task_id);
        })
        .catch(error => {
            showError('An error occurred while connecting to the server. Please try again.');
            console.error('Error:', error);
            resetForm();
        });
    });
    
    // Simulate progress
    function simulateProgress(taskId) {
        let progress = 0;
        const interval = setInterval(() => {
            progress += 5;
            progressBar.style.width = `${progress}%`;
            
            if (progress >= 100) {
                clearInterval(interval);
                checkConversionStatus(taskId);
            }
        }, 500);
    }
    
    // Check conversion status
    function checkConversionStatus(taskId) {
        fetch(`/api/status?task_id=${taskId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'completed') {
                    showResult(data.download_url, data.filename);
                } else if (data.status === 'failed') {
                    showError(data.error || 'Conversion failed. Please try again.');
                    resetForm();
                } else {
                    // Still processing, check again after a delay
                    setTimeout(() => checkConversionStatus(taskId), 1000);
                }
            })
            .catch(error => {
                showError('An error occurred while checking conversion status. Please try again.');
                console.error('Error:', error);
                resetForm();
            });
    }
    
    // Show result
    function showResult(url, filename) {
        statusContainer.style.display = 'none';
        resultContainer.style.display = 'block';
        
        downloadLink.href = url;
        downloadLink.download = filename;
        downloadLink.addEventListener('click', function() {
            setTimeout(resetForm, 2000);
        });
    }
    
    // Show error modal
    function showError(message) {
        errorMessage.textContent = message;
        errorModal.style.display = 'flex';
    }
    
    // Close error modal
    closeModalBtn.addEventListener('click', function() {
        errorModal.style.display = 'none';
    });
    
    closeModalX.addEventListener('click', function() {
        errorModal.style.display = 'none';
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target === errorModal) {
            errorModal.style.display = 'none';
        }
    });
});