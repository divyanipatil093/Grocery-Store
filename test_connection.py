from sql_connection import get_sql_connection

try:
    conn = get_sql_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    print("Connected to MySQL! Tables in your database:")
    for table in tables:
        print(table[0])
    cursor.close()
except Exception as e:
    print("Error connecting to MySQL:", e)