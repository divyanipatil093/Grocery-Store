from sql_connection import get_sql_connection
from cart_dao import get_cart, clear_cart

def place_order(user_id):
    cart_items = get_cart(user_id)
    if not cart_items:
        return None

    conn = get_sql_connection()
    cursor = conn.cursor()

    total_amount = sum([item[2]*item[3] for item in cart_items])
    cursor.execute("INSERT INTO orders (user_id, total_amount) VALUES (%s, %s)", (user_id, total_amount))
    order_id = cursor.lastrowid

    for item in cart_items:
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                       (order_id, item[0], item[3], item[2]))
        cursor.execute("UPDATE product SET stock=stock-%s WHERE product_id=%s", (item[3], item[0]))

    conn.commit()
    cursor.close()
    clear_cart(user_id)
    return order_id