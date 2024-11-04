// Event listener for the "Add Supplier Without Risk Documents" button
document.querySelector('.addWithoutRiskButton').addEventListener('click', function () {
    validateFormAndProceed(showConfirmationPopup);
});

// Event listener for the "Add Risk Documents" button
document.querySelector('.addRiskButton').addEventListener('click', function () {
    validateFormAndProceed(submitForm); // Proceed to submit form to server
});

// Function to validate form and proceed to specified action
function validateFormAndProceed(callback) {
    const form = document.getElementById('supplierForm');
    const requiredFields = form.querySelectorAll('[required]');
    let allFilled = true;

    // Check each required field
    requiredFields.forEach(field => {
        if (field.type === 'radio') {
            // For radio inputs, check if one is selected in each group
            const name = field.name;
            const radioGroup = form.querySelectorAll(`input[name="${name}"]:checked`);
            if (radioGroup.length === 0) {
                allFilled = false;
            }
        } else if (field.type === 'select-one') {
            // For dropdowns, ensure a value is selected
            if (field.value === '') {
                allFilled = false;
            }
        } else {
            // For other input types (e.g., text, email), check if they are empty
            if (field.value.trim() === '') {
                allFilled = false;
            }
        }
    });

    // Display error message if not all required fields are filled
    const errorMessage = document.getElementById('error-message');
    if (!allFilled) {
        errorMessage.style.display = 'block';
    } else {
        errorMessage.style.display = 'none';
        callback(); // Proceed to the specified action
    }
}

// Function to submit the form to the server and redirect to AddDocuments page
function submitForm() {
    // Set a hidden input field to indicate form submission with "Add Risk Documents" option
    const form = document.getElementById('supplierForm');
    const hiddenField = document.createElement("input");
    hiddenField.type = "hidden";
    hiddenField.name = "redirectToDocuments";
    hiddenField.value = "true";
    form.appendChild(hiddenField);

    // Submit the form to the server
    form.submit();
}

// Show confirmation popup
function showConfirmationPopup() {
    document.getElementById('confirmationOverlay').style.display = 'block';
    document.getElementById('confirmationPopup').style.display = 'block';
}

function closePopup() {
    document.getElementById('confirmationOverlay').style.display = 'none';
    document.getElementById('confirmationPopup').style.display = 'none';
}

function confirmAddSupplier() {
    closePopup();
    // Submit the form to save the supplier without risk documents
    document.getElementById('supplierForm').submit();
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
