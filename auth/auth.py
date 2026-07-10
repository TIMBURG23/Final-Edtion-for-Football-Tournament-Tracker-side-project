# auth/auth.py
"""
Authentication helpers: bcrypt password hashing and admin PIN check.
"""
import os
import bcrypt
import uuid
from dotenv import load_dotenv

load_dotenv()

ADMIN_PIN = os.getenv("DLS_ADMIN_PIN", "changeme")

def is_admin_pin_valid(pin: str) -> bool:
    return pin == ADMIN_PIN

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def check_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False

def generate_token() -> str:
    return str(uuid.uuid4())
