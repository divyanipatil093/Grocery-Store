# cart_dao.py
from db import get_db

def add_to_cart(user_id, product_id, quantity=1):
    """Adds a product to the user's cart or updates the quantity if it already exists."""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT quantity FROM cart WHERE user_id = %s AND product_id = %s",
            (user_id, product_id)
        )
        existing_quantity = cursor.fetchone()

        if existing_quantity:
            new_quantity = existing_quantity[0] + quantity
            cursor.execute(
                "UPDATE cart SET quantity = %s WHERE user_id = %s AND product_id = %s",
                (new_quantity, user_id, product_id)
            )
        else:
            cursor.execute(
                "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                (user_id, product_id, quantity)
            )
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error adding to cart: {e}")
        return False
    finally:
        cursor.close()

def get_cart(user_id):
    """Retrieves all products in a user's cart, joining with product details."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        query = """
            SELECT c.product_id, c.quantity, p.name, p.price, p.description, p.image_url
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.user_id = %s
        """
        cursor.execute(query, (user_id,))
        items = cursor.fetchall()
        
        grand_total = 0.0
        for item in items:
            item['subtotal'] = float(item['price']) * item['quantity']
            item['price'] = float(item['price'])
            grand_total += item['subtotal']
        
        return {'items': items, 'total': grand_total}
    except Exception as e:
        print(f"Error getting cart: {e}")
        return {'items': [], 'total': 0.0}
    finally:
        cursor.close()

def remove_from_cart(user_id, product_id):
    """Removes a single product from the user's cart."""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "DELETE FROM cart WHERE user_id = %s AND product_id = %s",
            (user_id, product_id)
        )
        db.commit()
        return cursor.rowcount > 0
    except Exception as e:
        db.rollback()
        print(f"Error removing from cart: {e}")
        return False
    finally:
        cursor.close()

def clear_cart(user_id):
    """Deletes all items from the user's cart."""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error clearing cart: {e}")
        return False
    finally:
        cursor.close()