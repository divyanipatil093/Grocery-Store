from db import get_db
from werkzeug.security import generate_password_hash, check_password_hash

def register_user(username, email, password):
    """Register a new user in the database."""
    db = get_db()
    cursor = db.cursor()
    try:
        # Check if email already exists
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return False  # Email already exists
        
        # Hash the password
        hashed_password = generate_password_hash(password)
        
        # Corrected SQL query to use 'name' instead of 'username'
        cursor.execute("""
            INSERT INTO users (name, email, password, role) 
            VALUES (%s, %s, %s, 'customer')
        """, (username, email, hashed_password))
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error registering user: {e}")
        return False
    finally:
        cursor.close()

def login_user(email, password):
    """Authenticate user login."""
    db = get_db()
    cursor = db.cursor()
    try:
        # Corrected SQL query to select 'name' instead of 'username'
        cursor.execute("""
            SELECT user_id, name, password, role 
            FROM users WHERE email = %s
        """, (email,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user[2], password):
            return (user[0], user[1], user[3])  # user_id, name, role
        return None
        
    except Exception as e:
        print(f"Error during login: {e}")
        return None
    finally:
        cursor.close()

def get_user_by_id(user_id):
    """Get user details by ID."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT user_id, name, email, role 
            FROM users WHERE user_id = %s
        """, (user_id,))
        return cursor.fetchone()
        
    except Exception as e:
        print(f"Error getting user: {e}")
        return None
    finally:
        cursor.close()