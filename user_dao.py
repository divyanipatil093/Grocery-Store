from sql_connection import get_sql_connection

def register_user(name, email, password):
    conn = get_sql_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
    conn.commit()
    cursor.close()

def login_user(email, password):
    conn = get_sql_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name FROM users WHERE email=%s AND password=%s", (email, password))
    user = cursor.fetchone()
    cursor.close()
    return user