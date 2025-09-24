# db.py
import mysql.connector
# Removed 'pooling' as it wasn't used
from flask import g
import os  # <-- Import the os library
from dotenv import load_dotenv

# --- MySQL Configuration ---
MYSQL_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
}

def get_db():
    """Get database connection, storing it in Flask's application context (g)."""
    if 'db' not in g or g.db.is_connected() is False:
        # FIX: Corrected DB_CONFIG to MYSQL_CONFIG
        g.db = mysql.connector.connect(**MYSQL_CONFIG) 
    return g.db

def close_db(e=None):
    """Close database connection after each request."""
    db = g.pop('db', None)
    if db is not None and db.is_connected():
        db.close()

def init_db():
    """Initialize database with required tables."""
    db = get_db()
    cursor = db.cursor()
    
    # NOTE: Using 'name' here to match your screenshot and fix the schema mismatch.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL, 
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role ENUM('customer', 'admin', 'user') DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            price DECIMAL(10, 2) NOT NULL,
            stock INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            cart_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            product_id INT NOT NULL,
            quantity INT DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
            UNIQUE KEY unique_user_product (user_id, product_id)
        )
    ''')
    
    # Orders, order_items, payments tables are assumed correct from your earlier post.
    # ... (SQL for orders, order_items, payments here) ...
    
    db.commit()
    cursor.close()
    print("Database tables initialized successfully!")