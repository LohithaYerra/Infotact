from flask import Flask, request, jsonify, render_template, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import sqlite3
import random
import string
from flask import send_file
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, 
             static_url_path='/static',
             static_folder='static')
CORS(app)

app.secret_key = "937f58b17a68f423b6b4faf41960f467b3bc06d52ae36670"

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

PASSWORD_FILE = "D:\\Shellovation\\PasswordGenerator\\PGBackend\\generated_passwords.txt"

# Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

@app.route("/check_users")
def check_users():
    users = User.query.all()
    num_users = len(users)
    user_details = [{"username": user.username, "password": user.password} for user in users]
    return jsonify({"total_users": num_users, "users": user_details})

# Serve the Login Page
@app.route("/")
def home():
    return render_template("login.html")  # Assuming you have a login.html template

# API: User Login
@app.route("/api/login", methods=["GET"])
def login_page():
    return jsonify({"message": "Use POST method to log in"}), 405  # Prevents unintended GET requests

@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user"] = user.username
            return jsonify({"message": "Login successful", "redirect":url_for('generator_page')}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401

    except Exception as e:
        print("Login Error:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/register", methods=["GET"])
def register_page():
    if request.method == "POST":
        return register()
    return render_template("register.html")


@app.route("/api/register", methods=["POST"])
def register():
    try: 
        data = request.get_json()
        print("Received Registration Data:", data)
        
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return jsonify({"error": "Missing required fields"}), 400

        if len(password) < 6 or len(password) > 64:
            return jsonify({"error": "Password must be 6-64 characters"}), 400

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({"error": "Username already exists"}), 400
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User created successfully", "redirect":url_for('home')}), 201

    except Exception as e:
        print("Registration Error:", str(e))
        return jsonify({"error": str(e)}), 500

# Serve the Password Generator Page
@app.route("/api/generator")
def generator_page():
    try:
        return render_template("generator.html")
    except:
        return jsonify({"error": "generator.html file is missing"}), 404

# Logout API
@app.route("/logout")
def logout():
    session.clear()  # Clear session
    response = jsonify({"message": "Logged out successfully"})
    
    # Cache invalidation headers
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response

# API: Password Generator
@app.route("/api/generate-password", methods=["POST"])
def generate_password():
    try:
        data = request.json
        length = data.get('length', 12)
        format_selected = data.get('format', "Alphanumeric + Special Characters")  # Default format

        if not isinstance(length, int) or length < 6 or length > 64:
            return jsonify({"error": "Password length must be between 6 and 64"}), 400

        # Define character sets based on user selection
        if format_selected == "Alphabet Only (Uppercase)":
            characters = string.ascii_uppercase
        elif format_selected == "Alphabet Only (Lowercase)":
            characters = string.ascii_lowercase
        elif format_selected == "Alphabet Only (Both Upper & Lower)":
            characters = string.ascii_letters
        elif format_selected == "Numerical Only":
            characters = string.digits
        elif format_selected == "Special Characters Only":
            characters = string.punctuation
        elif format_selected == "Alphanumeric":
            characters = string.ascii_letters + string.digits
        elif format_selected == "Alphanumeric + Special Characters":
            characters = string.ascii_letters + string.digits + string.punctuation
        elif format_selected == "Hexadecimal (0-9, A-F)":
            characters = string.hexdigits.upper()
        else:
            characters = string.ascii_letters + string.digits + string.punctuation  # Default

        password = ''.join(random.choice(characters) for _ in range(length))

        with open(PASSWORD_FILE, "a") as file:
            file.write(password + "\n")

        return jsonify({"password": password}), 200

    except Exception as e:
        print("Password Generation Error:", str(e))
        return jsonify({"error": str(e)}), 500

def ensure_password_file():
    if not os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, "w") as f:
            f.write("")  # Create an empty file

@app.route("/api/download-passwords", methods=["GET"])
def download_passwords():
    try:
        ensure_password_file()  # Ensure file exists before downloading
        return send_file(PASSWORD_FILE, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/clear-passwords", methods=["POST"])
def clear_passwords():
    try:
        ensure_password_file()  # Ensure file exists before clearing
        open(PASSWORD_FILE, "w").close()  # Clears the file
        return jsonify({"message": "Password file cleared successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
if __name__ == '__main__':
    app.run(debug=True)
