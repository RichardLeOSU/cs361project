// Toggle Info Tooltip
function ToggleInfo() {
    var infoBox = document.getElementById("InfoBox");
    infoBox.style.display = infoBox.style.display === "block" ? "none" : "block";
}

// Filter the table based on criteria
function filterTable(criteria) {
    const rows = document.querySelectorAll("#supplierTable tbody tr");
    rows.forEach(row => {
        const addDate = new Date(row.getAttribute("data-add-date"));
        const hasDocuments = row.getAttribute("data-has-documents") === "true";  // Interpret as a boolean
        const threeMonthsAgo = new Date();
        threeMonthsAgo.setMonth(threeMonthsAgo.getMonth() - 3);

        if (criteria === "recent") {
            // Show only recently added suppliers (within the last 3 months)
            row.style.display = addDate >= threeMonthsAgo ? "" : "none";
        } else if (criteria === "missing") {
            // Show only suppliers missing risk documents
            row.style.display = hasDocuments ? "none" : "";
        } else {
            // Show all rows if no criteria is selected
            row.style.display = "";
        }
    });
}

function sortTable(columnIndex) {
    const table = document.getElementById("supplierTable");
    const tbody = table.tBodies[0];
    const rows = Array.from(tbody.rows);
    let ascending = table.getAttribute("data-sort-order") !== "asc";

    // Set sort order attribute
    table.setAttribute("data-sort-order", ascending ? "asc" : "desc");

    // Reset all sort icons to neutral
    document.querySelectorAll(".sort-icon").forEach(icon => {
        icon.textContent = "↕"; // Default neutral icon
    });

    // Update the sort icon for the clicked column
    const header = table.tHead.rows[0].cells[columnIndex];
    const sortIcon = header.querySelector(".sort-icon");
    sortIcon.textContent = ascending ? "▲" : "▼"; // Arrow up for ascending, down for descending

    rows.sort((a, b) => {
        let cellA = a.cells[columnIndex].textContent.trim();
        let cellB = b.cells[columnIndex].textContent.trim();

        // Convert date or numeric columns
        if (columnIndex === 1) { // Date column (Add Date)
            cellA = new Date(cellA);
            cellB = new Date(cellB);
        } else if (columnIndex === 2) { // Numeric column (Risk Score)
            cellA = parseInt(cellA.split("/")[0]);
            cellB = parseInt(cellB.split("/")[0]);
        }

        // Compare and determine order
        if (cellA < cellB) return ascending ? -1 : 1;
        if (cellA > cellB) return ascending ? 1 : -1;
        return 0;
    });

    // Append sorted rows to tbody
    rows.forEach(row => tbody.appendChild(row));
}

