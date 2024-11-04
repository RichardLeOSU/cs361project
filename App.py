from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'vendors.db'
UPLOAD_FOLDER = 'uploaded_documents'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Helper function to calculate the risk score based on responses
def calculate_risk_score(form_data, hasRiskDocuments):
    score = 0
    if form_data['cybersecurityPolicy'] == "No":
        score += 20
    if form_data['isoCertified'] == "No":
        score += 15
    training = form_data['securityTraining']
    if training == "Biannually":
        score += 5
    elif training == "Annually":
        score += 10
    elif training == "Not Conducted":
        score += 20
    if form_data['incidentResponse'] == "No":
        score += 20
    access_level = form_data['dataAccessLevel']
    if access_level == "Limited access":
        score += 10
    elif access_level == "Full access":
        score += 20
    if form_data['complianceAudits'] == "No":
        score += 15
    if not hasRiskDocuments:
        score += 20
    return min(score, 100)


# Helper function to check if a supplier has documents in the uploaded_documents folder
def check_if_supplier_has_documents(supplier_id):
    # List all files in the uploaded_documents folder
    files_in_folder = os.listdir(UPLOAD_FOLDER)
    # Check if any file starts with the supplier's ID
    return any(file.startswith(f"{supplier_id}_") for file in files_in_folder)


# Dashboard Route
@app.route('/')
def Dashboard():
    conn = get_db_connection()

    # Query to get all suppliers from the database
    suppliers = conn.execute('SELECT * FROM suppliers').fetchall()
    conn.close()

    # Convert each supplier row to a dictionary and add `hasRiskDocuments` field
    supplier_data = []
    for supplier in suppliers:
        supplier_dict = dict(supplier)  # Convert sqlite3.Row to a dictionary
        supplier_dict['hasRiskDocuments'] = check_if_supplier_has_documents(supplier_dict['vendorId'])
        supplier_data.append(supplier_dict)

    # Calculate additional data for summary cards
    three_months_ago = datetime.now() - timedelta(days=90)
    recently_added = sum(
        1 for supplier in supplier_data if datetime.strptime(supplier['addDate'], "%m/%d/%y") >= three_months_ago
    )
    missing_documents_count = sum(1 for supplier in supplier_data if not supplier['hasRiskDocuments'])

    data = {
        "suppliers": len(supplier_data),
        "recentlyAdded": recently_added,
        "missingDocuments": missing_documents_count,
        "vendors": supplier_data
    }
    return render_template('Index.html', data=data)


@app.route('/AddVendor')
def AddVendor():
    return render_template('AddSupplier.html')


# Add supplier and calculate risk score
@app.route('/SaveSupplier', methods=['POST'])
def SaveSupplier():
    name = request.form['companyName']
    addDate = datetime.now().strftime("%m/%d/%y")
    hasRiskDocuments = False
    companyAddress = request.form['companyAddress']
    contactName = request.form['contactName']
    contactEmail = request.form['contactEmail']
    contactPhone = request.form['contactPhone']
    cybersecurityPolicy = request.form.get('cybersecurityPolicy', 'No')
    isoCertified = request.form.get('isoCertified', 'No')
    securityTraining = request.form['securityTraining']
    incidentResponse = request.form.get('incidentResponse', 'No')
    dataAccessLevel = request.form['dataAccessLevel']
    complianceAudits = request.form.get('complianceAudits', 'No')

    # Calculate risk score
    form_data = {
        'cybersecurityPolicy': cybersecurityPolicy,
        'isoCertified': isoCertified,
        'securityTraining': securityTraining,
        'incidentResponse': incidentResponse,
        'dataAccessLevel': dataAccessLevel,
        'complianceAudits': complianceAudits
    }
    riskScore = f"{calculate_risk_score(form_data, hasRiskDocuments)}/100"

    if not all([name, companyAddress, contactName, contactEmail, contactPhone]):
        flash("Please fill out all required fields.")
        return redirect(url_for('AddVendor'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO suppliers (
            name, addDate, riskScore, hasRiskDocuments, companyAddress, contactName, contactEmail, contactPhone,
            cybersecurityPolicy, isoCertified, securityTraining, incidentResponse, dataAccessLevel, complianceAudits
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, addDate, riskScore, hasRiskDocuments, companyAddress, contactName, contactEmail, contactPhone,
          cybersecurityPolicy, isoCertified, securityTraining, incidentResponse, dataAccessLevel, complianceAudits))
    conn.commit()
    supplier_id = cursor.lastrowid
    conn.close()

    # Redirect to AddDocuments page with supplier_id if requested
    if request.form.get("redirectToDocuments") == "true":
        return redirect(url_for('AddDocuments', supplier_id=supplier_id))

    return redirect(url_for('Dashboard'))


# Route for AddDocuments page with supplier_id
@app.route('/AddDocuments/<int:supplier_id>')
def AddDocuments(supplier_id):
    return render_template('AddDocuments.html', supplier_id=supplier_id)


@app.route('/upload_document/<int:supplier_id>', methods=['POST'])
def upload_document(supplier_id):
    files = request.files.getlist('fileUpload')
    if not files:
        flash("Please select files to upload.")
        return redirect(url_for('AddDocuments', supplier_id=supplier_id))

    conn = get_db_connection()
    try:
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                # Attempt to save the file
                try:
                    file.save(file_path)
                    print(f"File saved at: {file_path}")
                except Exception as e:
                    print(f"Error saving file {filename}: {e}")
                    flash(f"Error saving file {filename}")
                    return redirect(url_for('AddDocuments', supplier_id=supplier_id))

                # Attempt to insert the document record into the database
                try:
                    conn.execute('''
                        INSERT INTO documents (supplierId, fileName, filePath, uploadDate)
                        VALUES (?, ?, ?, ?)
                    ''', (supplier_id, filename, file_path, datetime.now().strftime("%Y-%m-%d")))
                    print(f"Record inserted into database for file {filename}")
                except Exception as e:
                    print(f"Error inserting record for {filename} into database: {e}")
                    flash(f"Error saving file metadata for {filename}")
                    return redirect(url_for('AddDocuments', supplier_id=supplier_id))
        conn.commit()
    finally:
        conn.close()

    flash("Upload successful!")
    return redirect(url_for('AddDocuments', supplier_id=supplier_id))


# Vendor profile route displaying supplier information and documents
@app.route('/VendorProfile/<int:vendorId>')
def VendorProfile(vendorId):
    conn = get_db_connection()
    vendor = conn.execute('SELECT * FROM suppliers WHERE vendorId = ?', (vendorId,)).fetchone()
    documents = conn.execute('SELECT * FROM documents WHERE supplierId = ?', (vendorId,)).fetchall()
    conn.close()
    if vendor is None:
        return "Vendor not found", 404

    return render_template('VendorProfile.html', vendor=vendor, documents=documents)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
