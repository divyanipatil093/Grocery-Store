from db import get_db # Changed

def make_payment(order_id, total, status, payment_method):
    conn = get_db() 
    cursor = conn.cursor()
    cursor.execute("INSERT INTO payment (order_id, amount, payment_method) VALUES (%s, %s, %s)", (order_id, amount, payment_method))
    conn.commit()
    cursor.close()