from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pickle
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ==============================
# Database Setup (SQLite)
# ==============================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ==============================
# User Model
# ==============================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# ==============================
# Load ML Model
# ==============================
MODEL_PATH = r"C:\Users\Aryya Manna\OneDrive\Desktop\student\model\student_score_model.pkl"

def load_model(path):
    if not os.path.exists(path):
        print(f"Error: Model file not found at {path}")
        return None
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

model = load_model(MODEL_PATH)

# ==============================
# Routes
# ==============================

@app.route("/")
def home():
    return render_template("index.html")

# ------------- SIGNUP -------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "error")
            return redirect(url_for("signup"))

        hashed_pw = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(username=username, email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        flash("Signup successful! You can now log in.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

# ------------- LOGIN -------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password.", "error")
    return render_template("login.html")

# ------------- LOGOUT -------------
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out successfully!", "info")
    return redirect(url_for("home"))

# ------------- PREDICTION FORM -------------
@app.route("/predict-form")
def predict_form():
    return render_template("predict.html")

# ------------- PREDICT RESULT -------------
@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return "<h3>Error: Prediction model is not loaded.</h3>"

    try:
        input_data = {
            "Gender": request.form.get("Gender"),
            "Study_Hours_per_Week": float(request.form.get("Study_Hours_per_Week")),
            "Attendance_Rate": float(request.form.get("Attendance_Rate")),
            "Past_Exam_Scores": float(request.form.get("Past_Exam_Scores")),
            "Parental_Education_Level": request.form.get("Parental_Education_Level"),
            "Internet_Access_at_Home": request.form.get("Internet_Access_at_Home"),
            "Extracurricular_Activities": request.form.get("Extracurricular_Activities"),
            "Final_Exam_Score": float(request.form.get("Final_Exam_Score")),
        }

        input_df = pd.DataFrame([input_data])
        prediction = model.predict(input_df)[0]

        return render_template("result.html", prediction=prediction, input_data=input_data)

    except Exception as e:
        return f"<h3>Error: {e}</h3>"

# ==============================
# Run App
# ==============================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
