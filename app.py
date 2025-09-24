from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import pooling

# DAO (Data Access Object) imports
from user_dao import register_user, login_user
from product_dao import (get_all_products, search_products, get_product_by_id, 
                         add_new_product, update_product_details, delete_product_by_id)
from cart_dao import add_to_cart, get_cart, remove_from_cart, clear_cart
from order_dao import place_order
from payment_dao import make_payment

# Create and configure the Flask app
app = Flask(__name__)
app.secret_key = "mysecret123"

# app.py
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db and hasattr(db, 'is_connected') and db.is_connected():
        db.close()

# ---------------- API ENDPOINTS (for JavaScript) ----------------

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    success = register_user(data.get('username'), data.get('email'), data.get('password'))
    if success:
        return jsonify({"message": "Registration successful"}), 201
    return jsonify({"error": "Email already exists"}), 409

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    # The login_user function in user_dao uses email, so we get it from the JSON data.
    user = login_user(data.get('email'), data.get('password'))
    if user:
        user_id, user_name, user_role = user
        session['user_id'] = user_id
        session['user_name'] = user_name
        session['user_role'] = user_role
        return jsonify({"message": "Login successful", "user": {"id": user_id, "name": user_name, "role": user_role}})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/products', methods=['GET'])
def api_products():
    products = get_all_products()
    return jsonify({"products": products})

@app.route('/api/products/add', methods=['POST'])
def api_add_product():
    data = request.get_json()
    new_id = add_new_product(data['name'], data['description'], data['price'], data['stock'])
    if new_id:
        return jsonify({"message": "Product added successfully!", "product_id": new_id}), 201
    return jsonify({"error": "Failed to add product"}), 500

@app.route('/api/products/update/<int:product_id>', methods=['POST'])
def api_update_product(product_id):
    data = request.get_json()
    success = update_product_details(product_id, data['name'], data['description'], data['price'], data['stock'])
    if success:
        return jsonify({"message": "Product updated successfully!"})
    return jsonify({"error": "Failed to update product"}), 500

@app.route('/api/products/delete/<int:product_id>', methods=['POST'])
def api_delete_product(product_id):
    success = delete_product_by_id(product_id)
    if success:
        return jsonify({"message": "Product deleted successfully!"})
    return jsonify({"error": "Failed to delete product"}), 500

@app.route('/api/cart/add', methods=['POST'])
def api_add_to_cart():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400

    if add_to_cart(session['user_id'], product_id, quantity):
        return jsonify({"message": "Product added to cart"}), 201
    return jsonify({"error": "Failed to add item"}), 400


@app.route('/api/cart', methods=['GET'])
def api_get_cart():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    cart_data = get_cart(user_id)
    
    return jsonify(cart_data), 200

@app.route('/api/cart/remove', methods=['POST'])
def api_remove_from_cart():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400
    
    if remove_from_cart(session['user_id'], product_id):
        return jsonify({"message": "Product removed from cart"}), 200
    
    return jsonify({"error": "Failed to remove item"}), 400

@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    delivery_address = data.get('delivery_address')
    payment_method = data.get('payment_method')
    
    if not delivery_address or not payment_method:
        return jsonify({"error": "Missing delivery address or payment method"}), 400

    # Step 1: Place the order from the cart
    order_id, total_amount = place_order(session['user_id'], delivery_address)
    
    if not order_id:
        return jsonify({"error": "Failed to create order, cart might be empty"}), 400

    # Step 2: Simulate payment and record it
    payment_success = make_payment(order_id, total_amount, 'Completed', payment_method)

    if payment_success:
        # Also clear the cart after a successful order
        clear_cart(session['user_id'])
        return jsonify({"message": "Order placed and payment successful!", "order_id": order_id}), 200
    else:
        # In a real application, you would handle this with better error logging and user feedback
        return jsonify({"error": "Order placed but payment failed. Please contact support.", "order_id": order_id}), 500

# ---------------- SERVER-SIDE RENDERED PAGES ----------------

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    products = get_all_products()
    return render_template('index.html', user_name=session.get('user_name'), products=products)

# This route renders the cart page. The data is loaded via JavaScript.
@app.route('/cart')
def show_cart():
    if 'user_id' not in session:
        flash("You need to be logged in to view your cart.", "error")
        return redirect(url_for('home'))
    
    user_id = session['user_id']
    cart_items = get_cart(user_id)

    return render_template('cart.html', cart=cart_items)

@app.route('/admin')
def admin_panel():
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for('home'))
    products = get_all_products()
    return render_template('admin.html', products=products)

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!")
    return redirect(url_for("home"))

@app.route("/search")
def search():
    query = request.args.get("query", "").strip()
    if not query:
        return redirect(url_for("home"))
    results = search_products(query)
    return render_template("search.html", results=results, query=query)

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash("Product not found", "error")
        return redirect(url_for("home"))
    all_products = get_all_products()
    related_products = [p for p in all_products if p['id'] != product_id]
    return render_template("product_detail.html", product=product, related_products=related_products)

# ---------------- ERROR HANDLERS ----------------

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True)