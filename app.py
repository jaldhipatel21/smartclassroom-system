from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import logging
from scripts.video_processor import process_video_for_attendance
  # Assuming you have a video_processor.py file
import csv
import cv2



app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use a strong random key in production

# Folder to save uploaded videos
UPLOAD_FOLDER = 'uploaded_videos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Database Setup (One-Time) ---
def init_db():
    with sqlite3.connect("users.db") as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
    print("Database initialized.")

# --- Helper Function ---
def get_user(username):
    with sqlite3.connect("users.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        if user:
            return {
                'id': user[0],
                'name': user[1],
                'username': user[2],
                'password': user[3],
                'role': user[4]
            }
        return None

# --- Routes ---

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = get_user(request.form['username'])
        if user and check_password_hash(user['password'], request.form['password']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            if user['role'] == 'admin':
                return redirect('/admin-register')
            elif user['role'] == 'professor':
                return redirect('/dashboard')
        return "Invalid login!"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/admin-register', methods=['GET', 'POST'])
def register():
    if 'role' not in session or session['role'] != 'admin':
        return "Access denied"
    
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        role = "professor"
        with sqlite3.connect("users.db") as conn:
            try:
                conn.execute("INSERT INTO users (name, username, password, role) VALUES (?, ?, ?, ?)",
                             (name, username, password, role))
                conn.commit()
                return "Professor registered successfully!"
            except sqlite3.IntegrityError:
                return "Username already exists."
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'role' not in session or session['role'] != 'professor':
        return "Access denied"
    return render_template('dashboard.html')

@app.route('/upload-video', methods=['GET', 'POST'])
def upload_video():
    if 'role' not in session or session['role'] != 'professor':
        return "Access denied"
    
    if request.method == 'POST':
        video_file = request.files.get('video_file')
        if not video_file:
            return "No file uploaded."

        filename = secure_filename(video_file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        video_file.save(filepath)

        # 👉 Call your video processing function here
        result = process_video_for_attendance(filepath, 'data/features_all.csv')


        return f"Video '{filename}' uploaded. Result: {result}"

    return render_template('upload_video.html')


@app.route('/attendance', methods=['POST'])
def attendance():
    selected_date = request.form.get('selected_date')
    selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
    formatted_date = selected_date_obj.strftime('%Y-%m-%d')

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name, time FROM attendance WHERE date = ?", (formatted_date,))
    attendance_data = cursor.fetchall()

    conn.close()

    if not attendance_data:
        return render_template('dashboard.html', selected_date=selected_date, no_data=True)
    
    return render_template('dashboard.html', selected_date=selected_date, attendance_data=attendance_data)

# --- Run App ---
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
