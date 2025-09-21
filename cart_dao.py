from db import get_db as get_sql_connection

def add_to_cart(user_id, product_id, quantity):
    conn = get_sql_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM cart WHERE user_id=%s AND product_id=%s", (user_id, product_id))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("UPDATE cart SET quantity=%s WHERE user_id=%s AND product_id=%s", (existing[0]+quantity, user_id, product_id))
    else:
        cursor.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)", (user_id, product_id, quantity))
    conn.commit()
    cursor.close()

# TO THIS:
def get_cart(user_id):
    conn = get_sql_connection()
    cursor = conn.cursor(dictionary=True)
    # We removed p.image_url and added a default path, aliased as image_url
    cursor.execute("""
        SELECT c.quantity, p.product_id, p.name, p.price, 
               'static/images/default.png' AS image_url
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id=%s
    """, (user_id,))
    items = cursor.fetchall()
    cursor.close()

    total = sum(item['price'] * item['quantity'] for item in items)
    
    return {"items": items, "total": total}

def remove_from_cart(user_id, product_id): # This function was missing from your file
    conn = get_sql_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM cart WHERE user_id = %s AND product_id = %s", (user_id, product_id))
        conn.commit()
        return cursor.rowcount > 0 # Return True if a row was deleted
    finally:
        cursor.close()
        # The connection will be closed automatically by app context teardown

def clear_cart(user_id):
    conn = get_sql_connection()