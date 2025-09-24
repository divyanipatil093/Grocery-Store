from db import get_db
from datetime import datetime

def make_payment(order_id, amount, status, payment_method):
    """Record a payment for an order."""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO payments (order_id, amount, status, payment_method, payment_date) 
            VALUES (%s, %s, %s, %s, %s)
        """, (order_id, amount, status, payment_method, datetime.now()))
        
        # If payment is successful, update order status
        if status == 'Completed':
            cursor.execute("""
                UPDATE orders SET status = 'confirmed' WHERE order_id = %s
            """, (order_id,))
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error processing payment: {e}")
        return False
    finally:
        cursor.close()

def get_payment_history(user_id):
    """Get payment history for a user."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT p.payment_id, p.order_id, p.amount, p.status, 
                   p.payment_method, p.payment_date, o.total_amount
            FROM payments p
            JOIN orders o ON p.order_id = o.order_id
            WHERE o.user_id = %s
            ORDER BY p.payment_date DESC
        """, (user_id,))
        return cursor.fetchall()
        
    except Exception as e:
        print(f"Error getting payment history: {e}")
        return []
    finally:
        cursor.close()

def update_payment_status(payment_id, status):
    """Update payment status."""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
            UPDATE payments SET status = %s WHERE payment_id = %s
        """, (status, payment_id))
        db.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        db.rollback()
        print(f"Error updating payment status: {e}")
        return False
    finally:
        cursor.close()