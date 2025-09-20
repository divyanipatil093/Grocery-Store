from sql_connection import get_sql_connection

def make_payment(order_id, amount, payment_method="Cash"):
    conn = get_sql_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO payment (order_id, amount, payment_method) VALUES (%s, %s, %s)", (order_id, amount, payment_method))
    conn.commit()
    cursor.close()