import mysql.connector
from mysql.connector import pooling
from flask import g

# --- MySQL Configuration ---
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Mysql@2006!', # <-- **VERIFY THIS PASSWORD**
    'database': 'grocery_db', 
}

# --- Connection Pool ---
try:
    db_pool = pooling.MySQLConnectionPool(pool_name="my_pool", pool_size=5, **MYSQL_CONFIG)
    print("MySQL Connection Pool created successfully.")
except mysql.connector.Error as err:
    print(f"Error creating connection pool: {err}")
    db_pool = None # Ensure db_pool is defined even on failure

def get_db():
    """Gets a connection from the pool."""
    if db_pool is None:
        raise RuntimeError("Database connection pool is not available.")
    
    db = getattr(g, '_database', None)
    if db is None:
        try:
            db = g._database = db_pool.get_connection()
        except mysql.connector.Error as err:
            raise RuntimeError(f"Could not connect to database: {err}")
    return db

def close_db(exception=None):
    """Closes the connection."""
    db = getattr(g, '_database', None)
    if db is not None and db.is_connected():
        db.close()