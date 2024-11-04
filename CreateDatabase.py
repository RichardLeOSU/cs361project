import sqlite3
import os
from datetime import datetime

# Constants
DATABASE = 'vendors.db'
UPLOAD_FOLDER = 'uploaded_documents'

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect(DATABASE)
c = conn.cursor()

# Create the suppliers table
c.execute('''
    CREATE TABLE IF NOT EXISTS suppliers (
        vendorId INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        addDate TEXT,
        riskScore TEXT,
        hasRiskDocuments BOOLEAN,
        companyAddress TEXT,
        contactName TEXT,
        contactEmail TEXT,
        contactPhone TEXT,
        cybersecurityPolicy TEXT,
        isoCertified TEXT,
        securityTraining TEXT,
        incidentResponse TEXT,
        dataAccessLevel TEXT,
        complianceAudits TEXT
    )
''')

# Create the documents table with a foreign key linking to the suppliers table
c.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        documentId INTEGER PRIMARY KEY AUTOINCREMENT,
        supplierId INTEGER,
        fileName TEXT,
        filePath TEXT,
        uploadDate TEXT,
        FOREIGN KEY (supplierId) REFERENCES suppliers(vendorId) ON DELETE CASCADE
    )
''')

# Insert ten sample supplier records
sample_suppliers = [
    ("Global Solutions LLC", "07/15/24", "51/100", True, "123 Global St.", "John Doe", "contact@global.com", "123-456-7890", "Yes", "Yes", "Quarterly", "Yes", "Full access", "Yes"),
    ("Prime Enterprises Inc.", "06/12/24", "72/100", False, "456 Prime Ave.", "Jane Smith", "info@prime.com", "987-654-3210", "No", "No", "Annually", "No", "Limited access", "No"),
    ("Blue Industries Corp.", "03/19/24", "44/100", True, "789 Blue St.", "Michael Johnson", "m.johnson@blueind.com", "123-789-4561", "Yes", "No", "Biannually", "Yes", "Limited access", "Yes"),
    ("Green Holdings Ltd.", "08/09/24", "39/100", False, "456 Green Ave.", "Emily Davis", "contact@greenholdings.com", "321-654-9870", "No", "Yes", "Annually", "No", "No access", "No"),
    ("Quantum Systems Group", "09/14/24", "88/100", True, "789 Quantum Rd.", "Robert Wilson", "r.wilson@quantum.com", "456-123-7890", "Yes", "Yes", "Quarterly", "Yes", "Full access", "Yes"),
    ("Silver Logistics Co.", "04/11/24", "63/100", False, "123 Silver Dr.", "Laura Thompson", "l.thompson@silverlogistics.com", "654-321-0987", "No", "No", "Not Conducted", "No", "Limited access", "No"),
    ("Infinite Networks International", "05/23/24", "28/100", True, "456 Infinite Loop", "Chris Evans", "c.evans@infinite.com", "789-456-1230", "Yes", "No", "Quarterly", "Yes", "No access", "Yes"),
    ("Pinnacle Services LLC", "02/17/24", "95/100", True, "789 Pinnacle Pl.", "Diana Prince", "d.prince@pinnacle.com", "852-741-9632", "Yes", "Yes", "Annually", "Yes", "Full access", "Yes"),
    ("United Partners Consulting", "10/20/23", "57/100", False, "321 United Blvd.", "Clark Kent", "kent@unitedpartners.com", "963-852-7410", "No", "No", "Biannually", "No", "Limited access", "No"),
    ("Dynamic Innovations Ventures", "01/26/24", "21/100", True, "987 Dynamic St.", "Bruce Wayne", "wayne@dynamic.com", "741-852-9630", "Yes", "Yes", "Quarterly", "Yes", "No access", "Yes")
]

c.executemany('''
    INSERT INTO suppliers (
        name, addDate, riskScore, hasRiskDocuments, companyAddress, contactName, contactEmail, contactPhone,
        cybersecurityPolicy, isoCertified, securityTraining, incidentResponse, dataAccessLevel, complianceAudits
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', sample_suppliers)

# Commit supplier data to ensure we can add document data linked to suppliers
conn.commit()

# Insert documents based on files in the `uploaded_documents` folder
current_date = datetime.now().strftime("%Y-%m-%d")

for file_name in os.listdir(UPLOAD_FOLDER):
    # Split the file name to get supplier ID and the rest of the file name
    try:
        supplier_id, document_name = file_name.split('_', 1)
        supplier_id = int(supplier_id)  # Convert supplier ID to integer
        file_path = os.path.join(UPLOAD_FOLDER, file_name)

        # Insert document record in the database
        c.execute('''
            INSERT INTO documents (supplierId, fileName, filePath, uploadDate)
            VALUES (?, ?, ?, ?)
        ''', (supplier_id, document_name, file_path, current_date))
        print(f"Inserted document '{document_name}' for supplier ID {supplier_id}")
    except ValueError:
        # Skip files that do not match the "{supplierId}_filename.ext" pattern
        print(f"Skipping file '{file_name}' - does not match required naming convention")

# Commit all document insertions
conn.commit()
conn.close()

print("Database created and populated with sample supplier and document data based on files in 'uploaded_documents' folder.")
