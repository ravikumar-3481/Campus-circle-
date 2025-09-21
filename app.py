from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import pandas as pd
import os

app = Flask(__name__)
CORS(app)  # frontend-backend connect karne ke liye

DB_NAME = "alumni.db"

# Database create table
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alumni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            graduation_year INTEGER,
            job_title TEXT,
            company TEXT,
            linkedin TEXT,
            phone TEXT,
            address TEXT
        )
        """)
        conn.commit()

init_db()

# Route: Add Alumni (from form page)
@app.route("/api/add_alumni", methods=["POST"])
def add_alumni():
    try:
        data = request.json
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO alumni (name, email, graduation_year, job_title, company, linkedin, phone, address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("name"),
                data.get("email"),
                data.get("graduation_year"),
                data.get("job_title"),
                data.get("company"),
                data.get("linkedin"),
                data.get("phone"),
                data.get("address")
            ))
            conn.commit()
        return jsonify({"message": "Alumni added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route: Get All Alumni (for show page)
@app.route("/api/alumni", methods=["GET"])
def get_alumni():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM alumni ORDER BY graduation_year DESC")
            rows = cursor.fetchall()
            alumni = [dict(row) for row in rows]
        return jsonify(alumni), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route: Export Alumni to Excel
@app.route("/api/export_alumni", methods=["GET"])
def export_alumni():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            df = pd.read_sql_query("SELECT * FROM alumni", conn)

        filename = "alumni_data.xlsx"
        df.to_excel(filename, index=False)

        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
