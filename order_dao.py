from db import get_db
from cart_dao import get_cart, clear_cart
from datetime import datetime

def place_order(user_id, delivery_address):
    """Place an order from the user's cart."""
    db = get_db()
    cursor = db.cursor()
    try:
        # Get cart items
        cart_data = get_cart(user_id)
        if not cart_data['items'] or cart_data['total'] <= 0:
            return None, 0
        
        # Create order
        cursor.execute("""
            INSERT INTO orders (user_id, total_amount, delivery_address, status, order_date) 
            VALUES (%s, %s, %s, 'pending', %s)
        """, (user_id, cart_data['total'], delivery_address, datetime.now()))
        
        order_id = cursor.lastrowid
        
        # Add order items
        for item in cart_data['items']:
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price) 
                VALUES (%s, %s, %s, %s)
            """, (order_id, item['product_id'], item['quantity'], item['price']))
        
        # Clear the cart
        # cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
        
        db.commit()
        return order_id, cart_data['total']
        
    except Exception as e:
        db.rollback()
        print(f"Error placing order: {e}")
        return None, 0
    finally:
        cursor.close()

def get_user_orders(user_id):
    """Get all orders for a specific user."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT order_id, total_amount, delivery_address, status, order_date 
            FROM orders 
            WHERE user_id = %s 
            ORDER BY order_date DESC
        """, (user_id,))
        return cursor.fetchall()
        
    except Exception as e:
        print(f"Error getting user orders: {e}")
        return []
    finally:
        cursor.close()

def get_order_details(order_id):
    """Get detailed information about a specific order."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Get order info
        cursor.execute("""
            SELECT o.order_id, o.user_id, o.total_amount, o.delivery_address, 
                   o.status, o.order_date, u.username, u.email
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            WHERE o.order_id = %s
        """, (order_id,))
        order = cursor.fetchone()
        
        if not order:
            return None
            
        # Get order items
        cursor.execute("""
            SELECT oi.product_id, oi.quantity, oi.price,
                   p.name as product_name, p.description
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
        """, (order_id,))
        items = cursor.fetchall()
        
        order['items'] = items
        return order
        
    except Exception as e:
        print(f"Error getting order details: {e}")
        return None
    finally:
        cursor.close()

def update_order_status(order_id, status):
    """Update the status of an order."""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
            UPDATE orders SET status = %s WHERE order_id = %s
        """, (status, order_id))
        db.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        db.rollback()
        print(f"Error updating order status: {e}")
        return False
    finally:
        cursor.close()