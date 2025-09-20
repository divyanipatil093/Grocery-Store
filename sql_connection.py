import mysql.connector

__cnx = None

def get_sql_connection():
    global __cnx
    if __cnx is None:
        __cnx = mysql.connector.connect(
            host="127.0.0.1",
            user="root",          # Replace with your MySQL username
            password="", # Replace with your MySQL password
            database="grocery_db"
        )
    return __cnx