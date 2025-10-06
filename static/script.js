function openTab(tabName) {
    // Hide all tab contents
    const tabContents = document.getElementsByClassName('tab-content');
    for (let tab of tabContents) {
        tab.classList.remove('active');
    }

    // Remove active class from all tab buttons
    const tabButtons = document.getElementsByClassName('tab-button');
    for (let button of tabButtons) {
        button.classList.remove('active');
    }

    // Show the selected tab content and activate the button
    document.getElementById(tabName).classList.add('active');
    event.currentTarget.classList.add('active');
}

function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function showError(message) {
    alert('Error: ' + message);
}

function showSuccess(message) {
    // You can implement a toast notification here
    console.log('Success: ' + message);
}

async function analyzeDocument() {
    const analysisType = document.getElementById('analysis_type').value;
    const text = document.getElementById('analyze_text').value;
    const fileInput = document.getElementById('file_upload');
    const file = fileInput.files[0];

    if (!text.trim() && !file) {
        showError('Please provide text or upload a file for analysis.');
        return;
    }

    showLoading();

    const formData = new FormData();
    formData.append('analysis_type', analysisType);
    
    if (file) {
        formData.append('file', file);
    } else {
        formData.append('text', text);
    }

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            displayAnalyzeResult(data);
        } else {
            showError(data.error);
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    } finally {
        hideLoading();
    }
}

async function draftDocument() {
    const docType = document.getElementById('doc_type').value;
    const requirements = document.getElementById('requirements').value;

    if (!requirements.trim()) {
        showError('Please provide requirements for the document.');
        return;
    }

    showLoading();

    const formData = new FormData();
    formData.append('doc_type', docType);
    formData.append('requirements', requirements);

    try {
        const response = await fetch('/draft', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            displayDraftResult(data);
        } else {
            showError(data.error);
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    } finally {
        hideLoading();
    }
}

function displayAnalyzeResult(data) {
    const resultCard = document.getElementById('analyze_result');
    const resultType = document.getElementById('result_type');
    const resultTime = document.getElementById('result_time');
    const resultContent = document.getElementById('analyze_content');

    // Format analysis type for display
    const typeMap = {
        'document_summary': 'Document Summary',
        'contract_review': 'Contract Review',
        'compliance_check': 'Compliance Check',
        'legal_advice': 'Legal Advice'
    };

    resultType.textContent = `Type: ${typeMap[data.analysis_type] || data.analysis_type}`;
    resultTime.textContent = `Analyzed: ${data.timestamp}`;
    resultContent.textContent = data.result;

    resultCard.classList.remove('hidden');
    resultCard.scrollIntoView({ behavior: 'smooth' });
}

function displayDraftResult(data) {
    const resultCard = document.getElementById('draft_result');
    const resultType = document.getElementById('draft_type');
    const resultTime = document.getElementById('draft_time');
    const resultContent = document.getElementById('draft_content');

    // Format document type for display
    const typeMap = {
        'nda': 'Non-Disclosure Agreement',
        'employment_contract': 'Employment Contract',
        'lease_agreement': 'Lease Agreement',
        'service_agreement': 'Service Agreement'
    };

    resultType.textContent = `Document: ${typeMap[data.doc_type] || data.doc_type}`;
    resultTime.textContent = `Generated: ${data.timestamp}`;
    resultContent.textContent = data.result;

    resultCard.classList.remove('hidden');
    resultCard.scrollIntoView({ behavior: 'smooth' });
}

async function copyToClipboard(elementId) {
    const content = document.getElementById(elementId).textContent;
    
    try {
        await navigator.clipboard.writeText(content);
        alert('Content copied to clipboard!');
    } catch (err) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = content;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        alert('Content copied to clipboard!');
    }
}

async function downloadDraft() {
    const content = document.getElementById('draft_content').textContent;
    
    try {
        const response = await fetch('/download_draft', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ content: content })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `legal_document_${new Date().toISOString().slice(0,10)}.txt`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            const error = await response.json();
            showError(error.error);
        }
    } catch (error) {
        showError('Download failed: ' + error.message);
    }
}

// File upload preview
document.getElementById('file_upload').addEventListener('change', function(e) {
    const file = e.target.files[0];
    const label = document.querySelector('.upload-label span');
    
    if (file) {
        label.textContent = `Selected: ${file.name}`;
        // Clear text area when file is selected
        document.getElementById('analyze_text').value = '';
    } else {
        label.textContent = 'Choose PDF, DOCX, or TXT file';
    }
});

// Clear file input when text area is used
document.getElementById('analyze_text').addEventListener('focus', function() {
    document.getElementById('file_upload').value = '';
    document.querySelector('.upload-label span').textContent = 'Choose PDF, DOCX, or TXT file';
});

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Legal Assistant initialized');
    
    // Add event listeners for Enter key in textareas
    document.getElementById('analyze_text').addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            analyzeDocument();
        }
    });
    
    document.getElementById('requirements').addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            draftDocument();
        }
    });
});