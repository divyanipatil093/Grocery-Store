from db import get_db as get_sql_connection # CHANGED
from cart_dao import get_cart, clear_cart

# This function had a small bug. It should accept address as an argument.
def place_order(user_id, address): # Added address parameter
    cart_data = get_cart(user_id)
    if not cart_data or not cart_data.get('items'):
        return None, 0 # Return None for order_id and 0 for total

    conn = get_sql_connection()
    cursor = conn.cursor()

    total_amount = cart_data.get('total', 0)
    
    # Use the address passed from the API
    cursor.execute("INSERT INTO orders (user_id, total_amount, shipping_address) VALUES (%s, %s, %s)", 
                   (user_id, total_amount, address))
    order_id = cursor.lastrowid

    for item in cart_data['items']:
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                       (order_id, item['product_id'], item['quantity'], item['price']))
        # Assuming your products table has a 'stock' column
        # cursor.execute("UPDATE products SET stock=stock-%s WHERE product_id=%s", (item['quantity'], item['product_id']))

    conn.commit()
    cursor.close()
    clear_cart(user_id)
    return order_id, total_amount