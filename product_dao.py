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
    # Implement actual search logic using WHERE...LIKE %s here
    return get_all_products()   