from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify, g
from werkzeug.security import generate_password_hash,check_password_hash
import mysql.connector 
from mysql.connector import pooling

# DAO imports - These files MUST be created
from user_dao import register_user, login_user
from product_dao import get_all_products, search_products
from cart_dao import add_to_cart, get_cart, remove_from_cart 
from order_dao import place_order
from payment_dao import make_payment

# Create Flask app
app = Flask(__name__)
app.secret_key = "mysecret123"


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g,'_database',None)
    if db is not None and db.is_connected():
        db.close()

# ---------------- API ENDPOINTS (Used by api.js) ----------------

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    name = data.get('username') # api.js sends 'username' for name
    email = data.get('email')
    password = data.get('password')
    
    success = register_user(name, email, password)
    
    if success:
        return jsonify({"message": "Registration successful"}), 201
    return jsonify({"error": "Email already exists"}), 409

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('username') # api.js sends 'username' for email
    password = data.get('password')

    user = login_user(email, password) # user is (user_id, user_name)

    if user:
        user_id, user_name = user
        # Set Flask session for backend cart/checkout authentication
        session['user_id'] = user_id
        session['user_name'] = user_name
        
        return jsonify({
            "message": "Login successful",
            "user": {"id": user_id, "name": user_name, "email": email}
        })
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/products', methods=['GET'])
def api_products():
    search_term = request.args.get('q')
    
    if search_term:
        products = search_products(search_term)
    else:
        products = get_all_products()
        
    return jsonify({"products": products})

@app.route('/api/cart/add', methods=['POST'])
def api_add_to_cart():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Please login to add items to cart"}), 401
    
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    success = add_to_cart(user_id, product_id, quantity)
    
    if success:
        return jsonify({"message": "Product added to cart"}), 201
    return jsonify({"error": "Failed to add item"}), 400

@app.route('/api/cart', methods=['GET'])
def api_get_cart():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    cart_data = get_cart(user_id) 
    return jsonify(cart_data)

@app.route('/api/cart/remove', methods=['POST'])
def api_remove_from_cart():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    product_id = data.get('product_id')
    
    success = remove_from_cart(user_id, product_id)
    
    if success:
        return jsonify({"message": "Product removed from cart"}), 200
    return jsonify({"error": "Item not found"}), 404

@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.get_json()
    address = data.get('address', 'Default Address') 
    payment_method = data.get('payment_method', 'Card')
    
    order_id, total = place_order(user_id, address) 
    
    if not order_id:
        return jsonify({"error": "Cart is empty or failed to place order"}), 400
        
    success = make_payment(order_id, total, 'Completed', payment_method)
    
    if success:
        return jsonify({"message": "Order placed successfully!", "order_id": order_id, "total": total})
    return jsonify({"error": "Payment failed"}), 500
    
# ---------------- SERVER-SIDE ROUTES ----------------

# The root route now redirects to /home
@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    # This route only renders the index.html template
    user_name = session.get('user_name')
    return render_template('index.html', user_name=user_name)

@app.route("/logout")
def logout():
    # This route is mainly for clearing the Flask session (backend logout)
    session.clear()
    flash("Logged out successfully!")
    return redirect(url_for("home"))

@app.route("/search")
def search():
    query = request.args.get("query")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE name LIKE ? OR category LIKE ?", 
                   ('%' + query + '%', '%' + query + '%'))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    if results:
        return render_template("search.html", results=results, query=query)
    else:
        return render_template("search.html", results=None, query=query)

 

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)