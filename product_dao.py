from sql_connection import get_sql_connection

def get_all_products():
    conn = get_sql_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, name, description, price, stock FROM products")
    products = cursor.fetchall()
    cursor.close()
    return products

def search_products(keyword):
    conn = get_sql_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, name, description, price, stock FROM products WHERE name LIKE %s", ('%' + keyword + '%',))
    products = cursor.fetchall()
    cursor.close()
    return products