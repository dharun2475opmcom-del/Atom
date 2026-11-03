"""
Database module for AquaGuard user authentication and management.
Uses SQLite3 for lightweight, zero-dependency, persistent storage.
"""

import os
import sqlite3
import hashlib
import hmac
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, List

# Default path to database file in data/
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "aquaguard.db"


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Get a database connection, ensuring the parent directory exists."""
    path = db_path or DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """
    Hash a password using PBKDF2-HMAC-SHA256 with 100,000 iterations and a unique salt.
    Returns (hex_hash, hex_salt).
    """
    if salt is None:
        salt_bytes = os.urandom(16)
        salt = salt_bytes.hex()
    else:
        salt_bytes = bytes.fromhex(salt)

    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt_bytes,
        100000
    )
    return pwd_hash.hex(), salt


def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    """Verify that the given password matches the expected hash."""
    calc_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(calc_hash, expected_hash)


def validate_username(username: str) -> Tuple[bool, str]:
    """Validate username rules: 3-30 chars, alphanumeric or underscores."""
    username = username.strip()
    if not username:
        return False, "Username cannot be empty."
    if len(username) < 3 or len(username) > 30:
        return False, "Username must be between 3 and 30 characters."
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores."
    return True, ""


def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email format."""
    email = email.strip()
    if not email:
        return False, "Email cannot be empty."
    email_regex = r"^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$"
    if not re.match(email_regex, email):
        return False, "Invalid email address format."
    return True, ""


def validate_password(password: str) -> Tuple[bool, str]:
    """Validate password strength (at least 6 characters)."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""


def init_db(db_path: Optional[Path] = None) -> None:
    """Initialize database tables and create demo user if empty."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    full_name TEXT,
                    role TEXT DEFAULT 'operator',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                );
            """)

            # Create an audit log table for user logins and actions
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
            """)

            # Seed demo user if no users exist
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM users")
            count = cur.fetchone()[0]
            if count == 0:
                pwd_hash, salt = hash_password("Aquaguard@2026")
                cur.execute("""
                    INSERT INTO users (username, email, password_hash, salt, full_name, role)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    "admin",
                    "admin@aquaguard.io",
                    pwd_hash,
                    salt,
                    "AquaGuard Administrator",
                    "admin"
                ))
    finally:
        conn.close()


def create_user(
    username: str,
    email: str,
    password: str,
    full_name: str = "",
    role: str = "operator",
    db_path: Optional[Path] = None
) -> Tuple[bool, str]:
    """
    Register a new user in the database.
    Returns (success: bool, message: str).
    """
    username = username.strip()
    email = email.strip().lower()
    full_name = full_name.strip()

    valid, msg = validate_username(username)
    if not valid:
        return False, msg

    valid, msg = validate_email(email)
    if not valid:
        return False, msg

    valid, msg = validate_password(password)
    if not valid:
        return False, msg

    pwd_hash, salt = hash_password(password)

    conn = get_connection(db_path)
    try:
        with conn:
            # Check unique username
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE LOWER(username) = LOWER(?)", (username,))
            if cur.fetchone():
                return False, f"Username '{username}' is already taken."

            # Check unique email
            cur.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (email,))
            if cur.fetchone():
                return False, f"Email '{email}' is already registered."

            cur.execute("""
                INSERT INTO users (username, email, password_hash, salt, full_name, role)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, email, pwd_hash, salt, full_name or username, role))

            user_id = cur.lastrowid
            conn.execute("""
                INSERT INTO user_activity (user_id, username, action, details)
                VALUES (?, ?, 'SIGNUP', 'New user registered')
            """, (user_id, username))

        return True, "Account created successfully! You can now log in."
    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()


def authenticate_user(
    username_or_email: str,
    password: str,
    db_path: Optional[Path] = None
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Verify user credentials against database.
    Returns (success: bool, user_data: dict | None, message: str).
    """
    identifier = username_or_email.strip()
    if not identifier:
        return False, None, "Please provide username or email."
    if not password:
        return False, None, "Please provide a password."

    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, username, email, password_hash, salt, full_name, role, created_at, last_login
            FROM users
            WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)
        """, (identifier, identifier))

        row = cur.fetchone()
        if not row:
            return False, None, "Invalid username/email or password."

        user_dict = dict(row)
        if not verify_password(password, user_dict["salt"], user_dict["password_hash"]):
            return False, None, "Invalid username/email or password."

        # Update last_login
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with conn:
            conn.execute("UPDATE users SET last_login = ? WHERE id = ?", (now_str, user_dict["id"]))
            conn.execute("""
                INSERT INTO user_activity (user_id, username, action, details)
                VALUES (?, ?, 'LOGIN', 'User logged in successfully')
            """, (user_dict["id"], user_dict["username"]))

        # Remove sensitive hash and salt before returning user object
        user_info = {
            "id": user_dict["id"],
            "username": user_dict["username"],
            "email": user_dict["email"],
            "full_name": user_dict["full_name"],
            "role": user_dict["role"],
            "created_at": user_dict["created_at"],
            "last_login": now_str
        }
        return True, user_info, "Login successful!"
    except sqlite3.Error as e:
        return False, None, f"Database error: {str(e)}"
    finally:
        conn.close()


def get_user_stats(db_path: Optional[Path] = None) -> Dict[str, Any]:
    """Get basic user counts and recent activities."""
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        total_users = cur.fetchone()[0]

        cur.execute("SELECT username, action, timestamp FROM user_activity ORDER BY id DESC LIMIT 5")
        recent_activity = [dict(r) for r in cur.fetchall()]

        return {
            "total_users": total_users,
            "recent_activity": recent_activity
        }
    except sqlite3.Error:
        return {"total_users": 0, "recent_activity": []}
    finally:
        conn.close()

