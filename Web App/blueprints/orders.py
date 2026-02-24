"""
Orders Blueprint for Gruha Alankara.
Handles furniture catalog, shopping cart, and order management.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from models import db, FurnitureItem, Order, OrderItem, Design
from datetime import datetime

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@orders_bp.route('/catalog')
def catalog():
    category = request.args.get('category')
    if category:
        items = FurnitureItem.query.filter_by(category=category).all()
    else:
        items = FurnitureItem.query.all()
    categories = db.session.query(FurnitureItem.category).distinct().all()
    return render_template('catalog.html', items=items, categories=[c[0] for c in categories])

@orders_bp.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    items_in_cart = []
    total = 0
    for item in cart_items:
        furniture = FurnitureItem.query.get(item['id'])
        if furniture:
            item_data = furniture.to_dict()
            item_data['quantity'] = item['quantity']
            item_data['subtotal'] = furniture.price * item['quantity']
            total += item_data['subtotal']
            items_in_cart.append(item_data)
    return render_template('cart.html', cart=items_in_cart, total=total)

@orders_bp.route('/cart/add/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    quantity = int(request.form.get('quantity', 1))
    cart = session.get('cart', [])
    
    # Check if already in cart
    found = False
    for item in cart:
        if item['id'] == item_id:
            item['quantity'] += quantity
            found = True
            break
    
    if not found:
        cart.append({'id': item_id, 'quantity': quantity})
    
    session['cart'] = cart
    flash('Item added to cart!', 'success')
    return redirect(url_for('orders.catalog'))

@orders_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        address = request.form.get('address')
        cart_items = session.get('cart', [])
        if not cart_items:
            flash('Your cart is empty.', 'error')
            return redirect(url_for('orders.catalog'))
            
        total = 0
        order_items = []
        for item in cart_items:
            furniture = FurnitureItem.query.get(item['id'])
            if furniture:
                price = furniture.price
                total += price * item['quantity']
                order_items.append(OrderItem(
                    furniture_id=furniture.id,
                    quantity=item['quantity'],
                    price=price
                ))
        
        order = Order(
            user_id=session['user_id'],
            total_amount=total,
            shipping_address=address,
            items=order_items
        )
        
        db.session.add(order)
        db.session.commit()
        session.pop('cart', None)
        flash('Order placed successfully!', 'success')
        return redirect(url_for('orders.my_orders'))
        
    return render_template('checkout.html')

@orders_bp.route('/my-orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=orders)

@orders_bp.route('/book-from-design/<int:design_id>')
@login_required
def book_from_design(design_id):
    design = Design.query.get_or_404(design_id)
    # logic to add design furniture to cart
    # for simplicity, we'll just redirect to catalog for now or add matched items
    flash('Restoring booking functionality...', 'info')
    return redirect(url_for('orders.catalog'))
