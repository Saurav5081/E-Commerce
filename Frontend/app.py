from flask import Flask, render_template, request, redirect, session, url_for, g
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'users.db'

# --- Product Data ---
products = [
    {"id": 1, "name": "Sporty Shoe", "price": 49.99, "image": "https://via.placeholder.com/150"},
    {"id": 2, "name": "Winter Hoodie", "price": 59.99, "image": "https://via.placeholder.com/150"},
    {"id": 3, "name": "Backpack", "price": 39.99, "image": "https://via.placeholder.com/150"}
]

# --- Database Helper ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );
        """)
        db.commit()

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html', products=products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            db.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            error = "Username already exists"
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('index'))
        else:
            error = "Invalid credentials"
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return "Product not found", 404

    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append(product)
    session.modified = True
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cart_items = session.get('cart', [])
    total = sum(item['price'] for item in cart_items)
    return render_template('cart.html', cart=cart_items, total=total)

# --- Init DB ---
if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)

