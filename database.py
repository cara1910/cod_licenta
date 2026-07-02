import sqlite3
from datetime import datetime,timedelta
from config import DATABASE


def get_connection():

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = get_connection()

    # ======================
    # DETECTIONS
    # ======================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT NOT NULL,
            detected_at TEXT NOT NULL,
            person_count INTEGER NOT NULL
        )
    """)
    
    try: 
        conn.execute("ALTER TABLE users ADD COLUMN reset_token TEXT")
    except sqlite3.OperationalError:
        pass
        
    try:
        conn.execute("ALTER TABLE users ADD COLUMN reset_token_expires TEXT")
    except sqlite3.OperationalError:
        pass

    # ======================
    # USERS
    # ======================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ==================================================
# DETECTIONS
# ==================================================

def save_detection(image_path, detected_at, person_count):

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO detections
        (image_path, detected_at, person_count)
        VALUES (?, ?, ?)
        """,
        (
            image_path,
            detected_at,
            person_count
        )
    )

    conn.commit()
    conn.close()


def get_all_detections():

    conn = get_connection()

    detections = conn.execute(
        """
        SELECT
            id,
            image_path,
            detected_at,
            person_count
        FROM detections
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return detections


# ==================================================
# USERS
# ==================================================

def create_user(username, email, password_hash):

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO users
        (username, email, password_hash)
        VALUES (?, ?, ?)
        """,
        (
            username,
            email,
            password_hash
        )
    )

    conn.commit()
    conn.close()


def get_user_by_username(username):

    conn = get_connection()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()

    conn.close()

    return user


def get_user_by_email(email):

    conn = get_connection()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        """,
        (email,)
    ).fetchone()

    conn.close()

    return user


def get_all_users():

    conn = get_connection()

    users = conn.execute(
        """
        SELECT *
        FROM users
        ORDER BY username
        """
    ).fetchall()

    conn.close()

    return users


def get_all_user_emails():

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT email
        FROM users
        """
    ).fetchall()

    conn.close()

    return [row["email"] for row in rows]


def save_reset_token(email, token, expires_at):
    conn = get_connection()

    conn.execute(
        """
        UPDATE users
        SET reset_token = ?, reset_token_expires = ?
        WHERE email = ?
        """,
        (token, expires_at, email)
    )

    conn.commit()
    conn.close()


def get_user_by_reset_token(token):
    conn = get_connection()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE reset_token = ?
        """,
        (token,)
    ).fetchone()

    conn.close()
    return user


def update_user_password(user_id, password_hash):
    conn = get_connection()

    conn.execute(
        """
        UPDATE users
        SET password_hash = ?,
            reset_token = NULL,
            reset_token_expires = NULL
        WHERE id = ?
        """,
        (password_hash, user_id)
    )

    conn.commit()
    conn.close()

def get_detections_by_date(selected_date):
    conn = get_connection()

    detections = conn.execute(
        """
        SELECT id, image_path, detected_at, person_count
        FROM detections
        WHERE detected_at LIKE ?
        ORDER BY detected_at DESC
        """,
        (selected_date + "%",)
    ).fetchall()

    conn.close()
    return detections
