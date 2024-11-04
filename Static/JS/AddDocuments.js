// Handle file upload
function handleFileUpload() {
    const fileInput = document.getElementById('fileUpload');
    const documentList = document.getElementById('documentList');
    documentList.innerHTML = ''; // Clear existing list

    Array.from(fileInput.files).forEach(file => {
        const row = document.createElement('tr');

        const nameCell = document.createElement('td');
        nameCell.textContent = file.name;

        const typeCell = document.createElement('td');
        typeCell.textContent = file.type || 'Unknown';

        const statusCell = document.createElement('td');
        statusCell.textContent = 'Pending Upload';

        row.appendChild(nameCell);
        row.appendChild(typeCell);
        row.appendChild(statusCell);

        documentList.appendChild(row);
    });
}

// Function to show the "Please wait" popup
function showWaitPopup() {
    document.getElementById('popupOverlay').style.display = 'flex';
    document.getElementById('popupMessage').textContent = "Please wait while your documents are being uploaded...";
    document.getElementById('popupActions').style.display = 'none'; // Hide close button during wait
}

// Function to show the success message in the popup
function showSuccessPopup() {
    document.getElementById('popupMessage').textContent = "Upload successful!";
    document.getElementById('popupActions').style.display = 'block'; // Show the close button
}

// Function to finalize uploads and submit form to server
function finalizeUpload() {
    const rows = document.querySelectorAll('#documentList tr');
    if (rows.length === 0) {
        showWarningMessage("Please add files to upload."); // Show warning if no files are uploaded
        return;
    }

    // Show wait popup
    showWaitPopup();

    // Submit the form to actually upload files to the server
    const uploadForm = document.getElementById('uploadForm');
    const formData = new FormData(uploadForm);

    fetch(uploadForm.action, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            // Update rows to show success status
            rows.forEach(row => {
                row.cells[2].textContent = 'Successful';
            });
            showSuccessPopup();
        } else {
            response.text().then(text => {
                console.error("Server response:", text);
                showWarningMessage("Failed to upload documents. Please try again.");
                closePopup();
            });
        }
    })
    .catch(error => {
        console.error("Error uploading documents:", error);
        showWarningMessage("An error occurred. Please try again.");
        closePopup();
    });
}

// Function to show a warning message if no files are uploaded
function showWarningMessage(message) {
    const warningMessage = document.getElementById('warningMessage');
    warningMessage.textContent = message;
    warningMessage.style.display = 'block';
}

// Function to close the popup and redirect to the dashboard
function closePopup() {
    document.getElementById('popupOverlay').style.display = 'none';
    window.location.href = '/'; // Redirect to the index (dashboard) page
}

// Toggle InfoBox visibility
function ToggleInfo() {
    const infoBox = document.getElementById('InfoBox');
    infoBox.style.display = (infoBox.style.display === 'block') ? 'none' : 'block';
}

// Close the InfoBox when clicking outside of it
window.addEventListener('click', function(event) {
    const infoBox = document.getElementById('InfoBox');
    const infoIcon = document.querySelector('.infoIcon');

    if (!infoBox.contains(event.target) && event.target !== infoIcon) {
        infoBox.style.display = 'none';
    }
});
