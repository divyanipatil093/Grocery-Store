from db import get_db

def get_all_products():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = "SELECT product_id AS id, name, price, description, 'static/images/default.png' as image_url FROM products"
    cursor.execute(query)
    products = cursor.fetchall()
    cursor.close()
    return products

def search_products(search_term):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Use LIKE to search for the term in both name and description
    query = """
        SELECT product_id AS id, name, price, description, 'static/images/default.png' as image_url 
        FROM products 
        WHERE name LIKE %s OR description LIKE %s
    """
    # The '%' symbols are wildcards for the LIKE query
    search_pattern = f"%{search_term}%"
    
    cursor.execute(query, (search_pattern, search_pattern))
    products = cursor.fetchall()
    cursor.close()
    
    return products

# In product_dao.py

def add_new_product(name, description, price, stock):
    """Inserts a new product into the database."""
    db = get_db()
    cursor = db.cursor()
    try:
        query = "INSERT INTO products (name, description, price, stock) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, description, price, stock))
        db.commit()
        return cursor.lastrowid # Return the ID of the new product
    except Exception as e:
        db.rollback()
        print(f"Error adding product: {e}")
        return None
    finally:
        cursor.close()

def update_product_details(product_id, name, description, price, stock):
    """Updates an existing product's details in the database."""
    db = get_db()
    cursor = db.cursor()
    try:
        query = """
            UPDATE products 
            SET name = %s, description = %s, price = %s, stock = %s 
            WHERE product_id = %s
        """
        cursor.execute(query, (name, description, price, stock, product_id))
        db.commit()
        return cursor.rowcount > 0 # Returns True if a row was updated
    except Exception as e:
        db.rollback()
        print(f"Error updating product: {e}")
        return False
    finally:
        cursor.close()

def delete_product_by_id(product_id):
    """Deletes a product from the database by its ID."""
    db = get_db()
    cursor = db.cursor()
    try:
        query = "DELETE FROM products WHERE product_id = %s"
        cursor.execute(query, (product_id,))
        db.commit()
        return cursor.rowcount > 0 # Returns True if a row was deleted
    except Exception as e:
        db.rollback()
        print(f"Error deleting product: {e}")
        return False
    finally:
        cursor.close()

def get_product_by_id(product_id):
    """Fetches a single product from the database by its ID."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        query = "SELECT product_id AS id, name, price, description, stock, 'static/images/default.png' as image_url FROM products WHERE product_id = %s"
        cursor.execute(query, (product_id,))
        product = cursor.fetchone()
        return product
    except Exception as e:
        print(f"Error fetching product by ID: {e}")
        return None
    finally:
        cursor.close()