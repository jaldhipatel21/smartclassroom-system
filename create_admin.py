import sqlite3
from werkzeug.security import generate_password_hash

# --- Change these values as needed ---
name = "Admin"
username = "admin"
password = "admin123"  # Choose a strong password!
role = "admin"

hashed_password = generate_password_hash(password)

with sqlite3.connect("users.db") as conn:
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (name, username, password, role) VALUES (?, ?, ?, ?)",
                       (name, username, hashed_password, role))
        conn.commit()
        print("Admin created successfully.")
    except sqlite3.IntegrityError:
        print("Admin already exists.")
