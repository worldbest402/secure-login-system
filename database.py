import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

# Database file lives in the project root
DB_PATH = Path(__file__).resolve().parent / "app.db"


def get_connection() -> sqlite3.Connection:
    """
    Create a new database connection.
    - row_factory returns dict-like rows for cleaner code.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Initialise the database with a secure users table.
    Matches Task 1 design:
    users(id, email UNIQUE, password_hash, role, created_at, failed_attempts, lock_until)
    """
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                failed_attempts INTEGER NOT NULL DEFAULT 0,
                lock_until TEXT DEFAULT NULL
            );
        """)
        conn.commit()


# -----------------------------
# Parameterised query functions
# -----------------------------

def create_user(email: str, password_hash: str, role: str = "user") -> None:
    """
    Insert a new user securely using parameterised SQL.
    """
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?);",
            (email, password_hash, role)
        )
        conn.commit()


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a user record by email securely using parameterised SQL.
    Returns dict-like row, or None.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, email, password_hash, role, failed_attempts, lock_until FROM users WHERE email = ?;",
            (email,)
        ).fetchone()
        return dict(row) if row else None


def update_failed_attempts(email: str, failed_attempts: int, lock_until: Optional[str]) -> None:
    """
    Update failed login attempts and lock timestamp (for brute-force resistance).
    """
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET failed_attempts = ?, lock_until = ? WHERE email = ?;",
            (failed_attempts, lock_until, email)
        )
        conn.commit()


def reset_failed_attempts(email: str) -> None:
    """
    Reset failed attempts after successful login.
    """
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET failed_attempts = 0, lock_until = NULL WHERE email = ?;",
            (email,)
        )
        conn.commit()

def is_account_locked(email: str) -> bool:
    """
    Check if an account is currently locked due to too many failed attempts.
    Returns False if unlocked or lock period has expired.
    """
    user = get_user_by_email(email)
    if not user:
        return False

    if user["lock_until"] is None:
        return False

    # Check if lock period has expired
    lock_until = datetime.fromisoformat(user["lock_until"])
    if datetime.now() > lock_until:
        # Automatically unlock
        reset_failed_attempts(email)
        return False

    return True


def increment_failed_attempts(email: str, max_attempts: int = 5, lockout_minutes: int = 15) -> None:
    """
    Increment failed login attempts and lock account if threshold exceeded.
    Defensive: Prevents brute-force attacks by locking after max_attempts.
    """
    user = get_user_by_email(email)
    if not user:
        return

    new_attempts = user["failed_attempts"] + 1
    lock_until = None

    if new_attempts >= max_attempts:
        # Lock account for specified duration
        lock_until = (datetime.now() + timedelta(minutes=lockout_minutes)).isoformat()

    update_failed_attempts(email, new_attempts, lock_until)