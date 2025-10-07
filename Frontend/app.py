from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(250), nullable=False)

# Routes
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            error = "Username already exists"
        else:
            hashed_pw = generate_password_hash(password)
            new_user = User(username=username, password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
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

    product = Product.query.get_or_404(product_id)
    item = {'id': product.id, 'name': product.name, 'price': product.price}

    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(item)
    session.modified = True
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cart_items = session.get('cart', [])
    total = sum(item['price'] for item in cart_items)
    return render_template('cart.html', cart=cart_items, total=total)

# Command to initialize DB and insert sample products
@app.cli.command("init-db")
def init_db():
    db.create_all()
    if Product.query.count() == 0:
        sample_products = [
            Product(name="Sporty Shoe", price=49.99, image="https://via.placeholder.com/150"),
            Product(name="Winter Hoodie", price=59.99, image="https://via.placeholder.com/150"),
            Product(name="Backpack", price=39.99, image="https://via.placeholder.com/150")
        ]
        db.session.bulk_save_objects(sample_products)
        db.session.commit()
        print("Database initialized with sample products.")
    else:
        print("Products already exist.")

