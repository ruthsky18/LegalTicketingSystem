// Legal Request Management System - Dynamic Form JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize form functionality
    initializeTicketForm();
    initializeFileUploads();
    initializeFormValidation();
});

function initializeTicketForm() {
    const natureSelect = document.getElementById('nature-select');
    const documentSection = document.getElementById('document-section');
    const contractingPartySection = document.getElementById('contracting-party-section');
    const documentField = document.querySelector('input[name="document_attached"]');
    const contractingPartyField = document.querySelector('textarea[name="details_of_contracting_party"]');
    
    if (natureSelect) {
        function toggleFields() {
            const selectedValue = natureSelect.value;
            
            if (selectedValue === 'for_review') {
                if (documentSection) {
                    documentSection.style.display = 'block';
                    documentSection.classList.add('fade-in');
                }
                if (contractingPartySection) {
                    contractingPartySection.style.display = 'block';
                    contractingPartySection.classList.add('fade-in');
                }
                if (documentField) {
                    documentField.required = true;
                }
                if (contractingPartyField) {
                    contractingPartyField.required = true;
                }
            } else {
                if (documentSection) {
                    documentSection.style.display = 'none';
                }
                if (contractingPartySection) {
                    contractingPartySection.style.display = 'none';
                }
                if (documentField) {
                    documentField.required = false;
                }
                if (contractingPartyField) {
                    contractingPartyField.required = false;
                }
            }
        }
        
        natureSelect.addEventListener('change', toggleFields);
        toggleFields(); // Initialize on page load
    }
}

function initializeFileUploads() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validate file type
                const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
                const maxSize = 10 * 1024 * 1024; // 10MB
                
                if (!allowedTypes.includes(file.type)) {
                    alert('Please upload only PDF, DOC, or DOCX files.');
                    input.value = '';
                    return;
                }
                
                if (file.size > maxSize) {
                    alert('File size must be less than 10MB.');
                    input.value = '';
                    return;
                }
                
                // Show file name
                const fileName = file.name;
                const label = input.nextElementSibling;
                if (label && label.tagName === 'LABEL') {
                    label.textContent = `Selected: ${fileName}`;
                    label.classList.add('text-success');
                }
            }
        });
    });
}

function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Add loading state
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Processing...';
                submitBtn.disabled = true;
            }
            
            // Validate required fields based on nature of engagement
            const natureSelect = form.querySelector('select[name="nature_of_engagement"]');
            if (natureSelect && natureSelect.value === 'for_review') {
                const documentField = form.querySelector('input[name="document_attached"]');
                const contractingPartyField = form.querySelector('textarea[name="details_of_contracting_party"]');
                
                if (documentField && !documentField.files.length) {
                    e.preventDefault();
                    alert('Document attachment is required for review requests.');
                    if (submitBtn) {
                        submitBtn.innerHTML = '<i class="bi bi-check-circle"></i> Submit Ticket';
                        submitBtn.disabled = false;
                    }
                    return;
                }
                
                if (contractingPartyField && !contractingPartyField.value.trim()) {
                    e.preventDefault();
                    alert('Details of contracting party are required for review requests.');
                    if (submitBtn) {
                        submitBtn.innerHTML = '<i class="bi bi-check-circle"></i> Submit Ticket';
                        submitBtn.disabled = false;
                    }
                    return;
                }
            }
        });
    });
}

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Auto-save functionality (optional)
function initializeAutoSave() {
    const forms = document.querySelectorAll('form[data-autosave]');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        const formId = form.dataset.autosave;
        
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                const formData = new FormData(form);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    data[key] = value;
                }
                
                localStorage.setItem(`autosave_${formId}`, JSON.stringify(data));
            });
        });
        
        // Load saved data on page load
        const savedData = localStorage.getItem(`autosave_${formId}`);
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                Object.keys(data).forEach(key => {
                    const input = form.querySelector(`[name="${key}"]`);
                    if (input && input.type !== 'file') {
                        input.value = data[key];
                    }
                });
            } catch (e) {
                console.error('Error loading autosaved data:', e);
            }
        }
    });
}

// Initialize auto-save if forms have the data-autosave attribute
document.addEventListener('DOMContentLoaded', function() {
    initializeAutoSave();
});

// Export functions for global use
window.LRMS = {
    showAlert,
    formatFileSize,
    initializeTicketForm,
    initializeFileUploads,
    initializeFormValidation
};




