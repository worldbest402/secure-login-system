# Secure Login & Authentication System

A university secure-programming project demonstrating the design, implementation and evaluation of a Flask-based authentication application. Built as a **local learning project**, not a production authentication service.

## Technologies

Python · Flask · SQLite · bcrypt · HTML/CSS · Bandit · OWASP ZAP

## Security controls implemented

- **Password hashing:** bcrypt with per-password salts; password hashes stored in SQLite instead of plaintext passwords.
- **Input validation:** server-side email format and password policy checks (10–128 characters, including a letter and a number).
- **SQL injection mitigation:** parameterised SQLite queries for user creation and lookup.
- **Authentication and access control:** login/logout flows and session checks before accessing `/dashboard`.
- **Login attempt controls:** tracks failed attempts for existing accounts and temporarily locks accounts after five failed attempts for 15 minutes.
- **Security event logging:** rotating log files for selected registration and authentication events.
- **Error handling:** generic user-facing error responses; Flask debug mode off by default.

## Design and threat modelling

The project used OWASP Top 10 and STRIDE to identify risks including credential compromise, injection, session misuse and unauthorised access. The application separates request handling (`app.py`), database access (`database.py`), password hashing (`security.py`) and input validation (`validators.py`).

## Testing and findings

The university assessment documented manual registration/login checks, unauthenticated dashboard access tests, attempted SQL injection, password-hash inspection, Bandit static analysis and OWASP ZAP Manual Explore. Following a debug-configuration fix, the report recorded a Bandit scan with no findings in the scanned application files. The ZAP exploration identified requests and highlighted opportunities to improve HTTP headers and cookie configuration. **These tests are limited in scope and do not establish that the application is free of vulnerabilities.**

## Run locally

1. Install Python 3 and create a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Set a persistent `SECRET_KEY` environment variable for your local session (recommended).
4. Start: `python app.py`
5. Open `http://127.0.0.1:5000` and register a test account.

The application creates `app.db` and `logs/security.log` locally. Both are excluded from version control.

## Limitations and next steps

This is a **learning prototype**. Planned improvements include CSRF protection for forms, stronger session cookie configuration, security headers, MFA, rate limiting beyond account lockout, and additional automated tests. Flask's built-in server is for local development only.

## Project context

Developed for a university Secure Programming module. The implementation and testing are presented as academic project work, not professional deployment experience.
