from flask import Blueprint, render_template, redirect, url_for, flash
from .models import Products, Cart, CartItem
from flask_login import login_required, current_user
from ecommerce import db



products_bp = Blueprint('products_bp', __name__, url_prefix='/product')

@products_bp.route('/products')
def products():
    return "this is products"

@products_bp.route('/product-details/<slug>')
def product_details(slug):
    product = Products.query.filter_by(slug=slug).first()
    return render_template('products/product_details.html', product=product, title=f'{product.title}')



@products_bp.route('/add-to-cart/<slug>')
@login_required
def add_to_cart(slug):
    user_cart = Cart.query.filter_by(user_id=current_user.id).first()
    if user_cart is None:
        user_cart = Cart(
            user_id=current_user.id,
        )
        db.session.add(user_cart)
        db.session.commit()
    print(user_cart)
    product = Products.query.filter_by(slug=slug).first_or_404()
    existing_cart_item = CartItem.query.filter_by(cart_id=user_cart.id ,product_id=product.id).first()
    if existing_cart_item:
        print('existing cart', existing_cart_item)
        existing_cart_item.quantity = +1
    else:
        cart_items = CartItem(
            product_id=product.id,
            cart_id = user_cart.id
        )
        db.session.add(cart_items)
        db.session.commit()
        print('New cart items', cart_items)
    return redirect(url_for('products_bp.user_cart'))



@products_bp.route('/user-cart')
@login_required
def user_cart():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if cart is None:
        cart = Cart(
            user_id=current_user.id,
        )
        db.session.add(cart)
        db.session.commit()

    cart_items = CartItem.query.filter_by(cart_id=cart.id)
    cart_total = cart.get_cart_total_price()
    return render_template('products/cart-items.html',cart_items=cart_items, title='Cart Items',cart_total=cart_total)


@products_bp.route('/remove-cart-item/<slug>')
@login_required
def remove_cartItem(slug):
    product = Products.query.filter_by(slug=slug).first()
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id).first()
    db.session.delete(cart_item)
    db.session.commit()
    flash('Your cart item removed!!!', 'info')
    return redirect(url_for('products_bp.user_cart'))