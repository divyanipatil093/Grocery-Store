from sql_connection import get_sql_connection

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

def get_cart(user_id):
    conn = get_sql_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT cart.cart_id, product.name, product.price, cart.quantity
        FROM cart
        JOIN product ON cart.product_id = product.product_id
        WHERE cart.user_id=%s
    """, (user_id,))
    cart_items = cursor.fetchall()
    cursor.close()
    return cart_items

def clear_cart(user_id):
    conn = get_sql_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id=%s", (user_id,))
    conn.commit()
    cursor.close()