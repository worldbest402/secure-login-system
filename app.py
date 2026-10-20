import os
import logging
import sqlite3
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.exceptions import HTTPException

from database import (
    init_db, 
    create_user, 
    get_user_by_email, 
    reset_failed_attempts,
    is_account_locked,
    increment_failed_attempts
)
from security import hash_password, verify_password
from validators import validate_registration_input, validate_login_input


# -----------------------
# Flask application setup
# -----------------------
app = Flask(__name__)

# Secret key for session security (environment variable preferred)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(32).hex())

# -----------------------
# Security logging setup
# Ensure logs directory exists and only attach file handler in the
# actual serving process (avoids debug reloader attaching handlers
# to the parent watcher process which doesn't handle requests).
# -----------------------
os.makedirs("logs", exist_ok=True)

if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    handler = RotatingFileHandler(
        "logs/security.log",
        maxBytes=1_000_000,
        backupCount=3
    )
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

# -----------------------
# Initialise database
# -----------------------
init_db()



# -----------------------
# Routes
# -----------------------
@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        try:
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")

            is_valid, _ = validate_login_input(email, password)
            if not is_valid:
                app.logger.warning(f"Failed login attempt for email: {email}")
                error = "Invalid login attempt."
            elif is_account_locked(email):
                # Account is locked due to too many failed attempts
                app.logger.warning(f"Login attempt on locked account: {email}")
                error = "Too many failed attempts. Account temporarily locked."
            else:
                user = get_user_by_email(email)

                if not user or not verify_password(password, user["password_hash"]):
                    # Increment failed attempts on failure
                    increment_failed_attempts(email)
                    app.logger.warning(f"Failed login attempt for email: {email}")
                    error = "Invalid login attempt."
                else:
                    # Successful login - reset failed attempts
                    reset_failed_attempts(email)
                    session["user_id"] = user["id"]
                    session["role"] = user["role"]

                    app.logger.info(f"Successful login for user ID: {user['id']}")
                    return redirect(url_for("dashboard"))
        except Exception as e:
            app.logger.error(f"Error during login: {str(e)}")
            error = "An unexpected error occurred. Please try again later."

    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        try:
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")

            is_valid, _ = validate_registration_input(email, password)
            if not is_valid:
                error = "Invalid registration details."
            else:
                existing_user = get_user_by_email(email)
                if existing_user:
                    app.logger.warning(f"Registration attempt with existing email: {email}")
                    error = "Registration failed."
                else:
                    # Hash password with error handling
                    password_hash = hash_password(password)
                    create_user(email, password_hash)

                    app.logger.info(f"New user registered with email: {email}")
                    return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            # Defensive: Handle race condition where email was created between check and insert
            app.logger.warning(f"Email already exists (race condition): {email}")
            error = "Registration failed."
        except Exception as e:
            app.logger.error(f"Error during registration: {str(e)}")
            error = "An unexpected error occurred. Please try again later."

    return render_template("register.html", error=error)


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# -----------------------
# Global error handling
# -----------------------
@app.errorhandler(Exception)
def handle_exception(e):
    # Don't catch HTTP exceptions (like 404) - let Flask handle them normally
    if isinstance(e, HTTPException):
        return e
    
    app.logger.error(f"Unhandled exception: {str(e)}")
    return (
        render_template(
            "login.html",
            error="An unexpected error occurred. Please try again later."
        ),
        500,
    )


# -----------------------
# Application entry point
# -----------------------
if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode)

