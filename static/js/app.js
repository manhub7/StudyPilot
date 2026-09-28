let selectedFile = null;

const pdfInput = document.getElementById('pdfInput');
const uploadBtn = document.getElementById('uploadBtn');
const clearBtn = document.getElementById('clearBtn');
const fileStatus = document.getElementById('fileStatus');
const documentEmpty = document.getElementById('documentEmpty');
const documentInfo = document.getElementById('documentInfo');
const documentName = document.getElementById('documentName');
const pageCount = document.getElementById('pageCount');
const chunkCount = document.getElementById('chunkCount');

pdfInput.addEventListener('change', () => {
    selectedFile = pdfInput.files[0] || null;
    if (!selectedFile) {
        fileStatus.classList.add('hidden');
        return;
    }
    if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
        selectedFile = null;
        pdfInput.value = '';
        showStatus('Please select a PDF file.');
        return;
    }
    fileStatus.textContent = `Selected: ${selectedFile.name}`;
    fileStatus.classList.remove('hidden');
});

uploadBtn.addEventListener('click', uploadPDF);
clearBtn.addEventListener('click', clearPDF);

async function uploadPDF() {
    if (!selectedFile) {
        showStatus('Please select a PDF first.');
        return;
    }

    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Indexing PDF...';

    try {
        const formData = new FormData();
        formData.append('file', selectedFile);
        const response = await fetch('/api/upload', { method: 'POST', body: formData });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Upload failed.');

        fileStatus.textContent = `✓ ${data.filename} · ${data.pages} pages · ${data.chunks} chunks indexed`;
        fileStatus.classList.remove('hidden');
        updateDocumentInfo(data);
    } catch (error) {
        showStatus(`Error: ${error.message}`);
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = 'Upload & Analyze';
    }
}

function updateDocumentInfo(data) {
    documentEmpty.classList.add('hidden');
    documentInfo.classList.remove('hidden');
    documentName.textContent = data.filename || '—';
    pageCount.textContent = data.pages ?? 0;
    chunkCount.textContent = data.chunks ?? 0;
}

async function clearPDF() {
    clearBtn.disabled = true;
    try {
        const response = await fetch('/api/clear', { method: 'POST' });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Could not clear document.');

        selectedFile = null;
        pdfInput.value = '';
        fileStatus.classList.add('hidden');
        documentEmpty.classList.remove('hidden');
        documentInfo.classList.add('hidden');
        documentName.textContent = '—';
        pageCount.textContent = '0';
        chunkCount.textContent = '0';
    } catch (error) {
        showStatus(`Error: ${error.message}`);
    } finally {
        clearBtn.disabled = false;
    }
}

function showStatus(message) {
    fileStatus.textContent = message;
    fileStatus.classList.remove('hidden');
}
