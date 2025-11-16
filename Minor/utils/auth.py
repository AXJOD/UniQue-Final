"""
Authentication utilities for Streamlit app
"""

import bcrypt
from services.database import Database

db = Database()

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_user(username: str, password: str, role: str, email: str = None) -> bool:
    """Create a new user - returns True if successful"""
    try:
        # Database.create_user now handles password hashing internally
        user_id = db.create_user(username, password, role, email)
        return user_id is not None
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def verify_user(username: str, password: str) -> dict:
    """Verify user credentials and return user data"""
    user = db.get_user(username)
    if user and verify_password(password, user['password_hash']):
        return user
    return None

def check_admin(user_id: str) -> bool:
    """Check if user is admin"""
    user = db.get_user_by_id(user_id)
    return user and user['role'] == 'admin'