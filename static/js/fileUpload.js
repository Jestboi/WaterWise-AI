class FileUploadHandler {
    constructor() {
        this.fileUpload = document.getElementById('file-upload');
        this.filePreview = document.getElementById('file-preview');
        this.removeFileBtn = document.getElementById('remove-file');
        this.fileNameDisplay = this.filePreview.querySelector('.file-name');
        this.currentFile = null;
        this.fileContent = null;
        this.minFileSize = 5;  // 5 bytes
        this.maxFileSize = 50 * 1024 * 1024; // 50MB in bytes

        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Handle file selection
        this.fileUpload.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Handle file removal
        this.removeFileBtn.addEventListener('click', () => this.removeFile());
    }

    async handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            // Validate file type
            const allowedTypes = ['.pdf', '.doc', '.docx', '.txt'];
            const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
            
            if (!allowedTypes.includes(fileExtension)) {
                alert('Please select a valid file type (PDF, DOC, DOCX, or TXT)');
                this.removeFile();
                return;
            }

            // Check minimum file size
            if (file.size < this.minFileSize) {
                alert(`File size must be at least 5 bytes. Current size: ${file.size} bytes`);
                this.removeFile();
                return;
            }

            // Check maximum file size
            if (file.size > this.maxFileSize) {
                alert(`File size should not exceed 50MB. Current size: ${this.formatFileSize(file.size)}`);
                this.removeFile();
                return;
            }

            try {
                // Read file content
                const fileContent = await this.readFileContent(file);
                this.fileContent = fileContent;
                this.currentFile = file;

                // Update UI
                this.fileNameDisplay.textContent = file.name;
                this.filePreview.classList.remove('hidden');
                this.fileUpload.value = ''; // Reset file input
            } catch (error) {
                console.error('Error reading file:', error);
                alert('Error reading file. Please try again.');
                this.removeFile();
            }
        }
    }

    formatFileSize(bytes) {
        if (bytes < 1024) {
            return bytes + ' bytes';
        } else if (bytes < 1024 * 1024) {
            return (bytes / 1024).toFixed(2) + ' KB';
        } else {
            return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
        }
    }

    readFileContent(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(e);
            reader.readAsText(file);
        });
    }

    showFilePreview() {
        if (this.currentFile) {
            this.fileNameDisplay.textContent = `${this.currentFile.name} (${this.formatFileSize(this.currentFile.size)})`;
            this.filePreview.classList.remove('hidden');
        }
    }

    removeFile() {
        this.currentFile = null;
        this.fileContent = null;
        this.fileNameDisplay.textContent = '';
        this.filePreview.classList.add('hidden');
        this.fileUpload.value = ''; // Reset file input
    }

    getCurrentFile() {
        return this.currentFile;
    }

    getFileContent() {
        return this.fileContent || null;
    }
}

// Initialize file upload handler when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.fileUploadHandler = new FileUploadHandler();
});
