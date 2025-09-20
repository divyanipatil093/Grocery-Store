from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'grocery_website_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grocery_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------------
# Database Models
# ---------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))
    stock_quantity = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    payment_status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ---------------------
# Web Routes (HTML)
# ---------------------





@app.route("/")
def home():
    if "user_id" in session:
        return render_template("index.html", user_name=session["username"])
    return redirect(url_for("login_page"))

@app.route("/login", methods=["GET", "POST"])
def login_page():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Logged in successfully!")
            return redirect(url_for("home"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)

@app.route("/register", methods=["GET", "POST"])
def register_page():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            error = "Username already exists"
        elif User.query.filter_by(email=email).first():
            error = "Email already exists"
        else:
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password)
            )
            db.session.add(user)
            db.session.commit()
            flash("Registration successful! Please log in.")
            return redirect(url_for("login_page"))

    return render_template("register.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!")
    return redirect(url_for("login_page"))

# ---------------------
# API Routes
# ---------------------

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing data'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password'])
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing data'}), 400

    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({'message': 'Login successful', 'user': {'id': user.id, 'username': user.username}}), 200

    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/products')
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'price': p.price,
        'image_url': p.image_url,
        'stock_quantity': p.stock_quantity,
        'is_featured': p.is_featured
    } for p in products])

@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'products': []})

    products = Product.query.filter(Product.name.contains(query)).limit(10).all()
    return jsonify({
        'products': [{
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'image_url': p.image_url
        } for p in products]
    })

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401

    data = request.get_json()
    product_id = str(data.get('product_id'))
    quantity = data.get('quantity', 1)

    if not product_id:
        return jsonify({'error': 'Missing product_id'}), 400

    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']
    cart[product_id] = cart.get(product_id, 0) + quantity
    session['cart'] = cart

    return jsonify({'message': 'Product added to cart'}), 200

@app.route('/api/cart')
def get_cart():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401

    cart = session.get('cart', {})
    items = []
    total = 0

    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product:
            subtotal = product.price * qty
            total += subtotal
            items.append({
                'product_id': product.id,
                'name': product.name,
                'price': product.price,
                'quantity': qty,
                'image_url': product.image_url,
                'item_total': subtotal
            })

    return jsonify({'items': items, 'total': total})

@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    data = request.get_json()
    product_id = str(data['product_id'])
    
    cart = session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
        session['cart'] = cart
    
    return jsonify({'message': 'Product removed from cart'}), 200

# ---------------------
# Initialize DB and Seed Products
# ---------------------

def init_db():
    with app.app_context():
        db.create_all()
        if Product.query.count() == 0:
            products = [
                Product(name='Fresh Tomatoes', description='Red ripe tomatoes', price=2.99, stock_quantity=100, is_featured=True, image_url='/static/images/tomatoes.jpg'),
                Product(name='Green Lettuce', description='Fresh green lettuce', price=1.99, stock_quantity=50, image_url='/static/images/lettuce.jpg'),
                Product(name='Red Apples', description='Sweet red apples', price=3.49, stock_quantity=75, is_featured=True, image_url='/static/images/apples.jpg'),
                Product(name='Bananas', description='Fresh yellow bananas', price=1.29, stock_quantity=100, image_url='/static/images/bananas.jpg'),
                Product(name='Milk 1L', description='Fresh whole milk', price=2.49, stock_quantity=30, image_url='/static/images/milk.jpg'),
                Product(name='Bread', description='Fresh white bread', price=1.99, stock_quantity=40, image_url='/static/images/bread.jpg'),
                Product(name='Carrots', description='Fresh orange carrots', price=1.79, stock_quantity=80, image_url='/static/images/carrots.jpg'),
                Product(name='Chicken Breast', description='Fresh chicken breast', price=5.99, stock_quantity=25, is_featured=True, image_url='/static/images/chicken.jpg')
            ]
            for product in products:
                db.session.add(product)
            db.session.commit()

# ---------------------
# Run the App
# ---------------------

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='127.0.0.1', port=5000)