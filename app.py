from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import uuid
import pandas as pd
from datetime import datetime
import io

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database setup
def init_db():
    conn = sqlite3.connect('alumni.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS alumni 
                 (id TEXT PRIMARY KEY, name TEXT, email TEXT, graduation_year INTEGER, 
                  job_title TEXT, company TEXT, linkedin TEXT, phone TEXT, address TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Endpoint to add alumni
@app.route('/api/alumni', methods=['POST'])
def add_alumni():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    graduation_year = data.get('graduation_year')
    job_title = data.get('job_title')
    company = data.get('company')
    linkedin = data.get('linkedin')
    phone = data.get('phone')
    address = data.get('address')

    if not all([name, email, graduation_year]):
        return jsonify({'error': 'Name, email, and graduation year are required'}), 400

    conn = sqlite3.connect('alumni.db')
    c = conn.cursor()
    c.execute("SELECT email FROM alumni WHERE email = ?", (email,))
    if c.fetchone():
        conn.close()
        return jsonify({'error': 'Email already exists'}), 400

    alum_id = str(uuid.uuid4())
    c.execute("INSERT INTO alumni (id, name, email, graduation_year, job_title, company, linkedin, phone, address) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (alum_id, name, email, graduation_year, job_title or None, company or None, linkedin or None, phone or None, address or None))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Alumni added successfully', 'id': alum_id}), 201

# Endpoint to get all alumni
@app.route('/api/alumni', methods=['GET'])
def get_alumni():
    conn = sqlite3.connect('alumni.db')
    c = conn.cursor()
    c.execute("SELECT * FROM alumni")
    alumni = c.fetchall()
    conn.close()

    alumni_list = [
        {
            'id': row[0], 'name': row[1], 'email': row[2], 'graduation_year': row[3],
            'job_title': row[4], 'company': row[5], 'linkedin': row[6], 'phone': row[7], 'address': row[8]
        } for row in alumni
    ]
    return jsonify(alumni_list)

# Endpoint to export alumni to Excel
@app.route('/api/export_alumni', methods=['GET'])
def export_alumni():
    conn = sqlite3.connect('alumni.db')
    query = "SELECT * FROM alumni"
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Create an in-memory file
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    # Generate filename with current date and time
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'alumni_data_{current_time}.xlsx'

    # Return file for download
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        attachment_filename=filename
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)