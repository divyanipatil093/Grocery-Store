from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash,check_password_hash
import sqlite3 
from flask import g

# DAO imports
from user_dao import register_user, login_user
from product_dao import get_all_products, search_products
from cart_dao import add_to_cart, get_cart
from order_dao import place_order
from payment_dao import make_payment

# Create Flask app
app = Flask(__name__)
app.secret_key = "mysecret123"  # required for flash messages and sessions



DATABASE ="instance/grocery_db.sqlite"
def get_db():
    db = getattr(g,'_database',None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g,'_database',None)
    if db is not None:
        db.close()




def register_user(name, email, password):
    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password)),
        )
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def login_user(email, password):
    db = get_db()
    user = db.execute(
        "SELECT id, name, password FROM users WHERE email = ?", (email,)
    ).fetchone()
    if user and check_password_hash(user["password"], password):
        return (user["id"], user["name"])
    return None


    


# ---------------- LOGIN / SIGNUP ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == "POST":
        action = request.form.get('action')
        
        if action == 'signup':
            # Register user
            success=register_user(
                request.form['name'], 
                request.form['email'], 
                request.form['password']
            )
            if success:
                flash("Registered successfully! Please log in.")

        else:
            error="Email already exists!"

        elif action == 'login':
            # Login user
            user = login_user(request.form['email'], request.form['password'])
            if user:
                session['user_id'] = user[0]
                session['user_name'] = user[1]
                flash("Logged in successfully!")
                return redirect(url_for("home"))
            else:
                error = "Invalid credentials"
    
    return render_template('login.html', error=error)


# ---------------- HOME PAGE ----------------
@app.route('/home')
def home():
    if 'user_id' not in session:
        if not session.get("already_warned"):
            flash("Please log in first!")
            session["already_warned"]=True
        return redirect(url_for("login"))
        session.pop("already_warned",None)

    # Example: load products for homepage
    #products = get_all_products()
    return render_template('index.html', user_name=session['user_name'])


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!")
    return redirect(url_for("login"))


# ---------------- FLASH TEST ROUTES ----------------
@app.route("/test_flash", strict_slashes=False)
def test_flash():
    flash("Secret Key is Working! 🎉")
    return redirect(url_for("login"))

@app.route("/test_flash_direct")
def test_flash_direct():
    flash("Secret Key is Working!")
    return render_template("test_flash.html")


@app.route("/check")
def check():
    return "Home route is Working!"



# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)