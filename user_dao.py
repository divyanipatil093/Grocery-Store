from db import get_db # CHANGED
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

def register_user(name, email, password):
    db = get_db()
    cursor = db.cursor()
    try:
        hashed_password = generate_password_hash(password)
        # Use %s placeholders for MySQL
        query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (name, email, hashed_password))
        db.commit()
        return True
    except mysql.connector.IntegrityError:
        return False
    finally:
        cursor.close()

def login_user(email, password):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    query = "SELECT user_id, name, password FROM users WHERE email = %s"
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    cursor.close()
    
    if user and check_password_hash(user["password"], password):
        return (user["user_id"], user["name"]) 
    return None