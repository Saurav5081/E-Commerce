from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session

# Sample product data
products = [
    {"id": 1, "name": "Sporty Shoe", "price": 49.99, "image": "https://via.placeholder.com/150"},
    {"id": 2, "name": "Winter Hoodie", "price": 59.99, "image": "https://via.placeholder.com/150"},
    {"id": 3, "name": "Backpack", "price": 39.99, "image": "https://via.placeholder.com/150"}
]

@app.route('/')
def index():
    return render_template('index.html', products=products)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
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
    cart_items = session.get('cart', [])
    total = sum(item['price'] for item in cart_items)
    return render_template('cart.html', cart=cart_items, total=total)

if __name__ == '__main__':
    app.run(debug=True)

