from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from .models import Products, Cart, CartItem, ShippingAddress, PlacedOrder, PlacedOrderItem
from flask_login import login_required, current_user
from ecommerce import db
from .forms import ShippingAddressForm
from ecommerce.payments.routes import retrieve_stripe_saved_payment_methods_by_customer_id



products_bp = Blueprint('products_bp', __name__, url_prefix='/product')

# @products_bp.route('/products')
# def products():
#     return "this is products"

@products_bp.route('/product-details/<slug>')
def product_details(slug):
    product = Products.query.filter_by(slug=slug).first()
    return render_template('products/product_details.html', product=product, title=f'{product.title}')



@products_bp.route('/add-to-cart/<slug>')
def add_to_cart(slug):
    # retrive user cart or crete to add product or item to the cart
    if not current_user.is_authenticated:
        return redirect(url_for('user_bp.user_login'))
    user_cart = Cart.query.filter_by(user_id=current_user.id).first()
    if user_cart is None:
        user_cart = Cart(
            user_id=current_user.id,
        )
        db.session.add(user_cart)
        db.session.commit()
    # print(user_cart)

    #targeted product that user want to add in the cart
    product = Products.query.filter_by(slug=slug).first_or_404()

    #check if the product already added to the cart if not then added to cart
    existing_cart_item = CartItem.query.filter_by(cart_id=user_cart.id ,product_id=product.id).first()
    if existing_cart_item:
        existing_cart_item.quantity = existing_cart_item.quantity +1
    else:
        cart_items = CartItem(
            product_id=product.id,
            cart_id = user_cart.id
        )
        db.session.add(cart_items)
    db.session.commit()
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
    # print(cart_items)
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


def save_shipping_address(addressForm):
    new_address = ShippingAddress(
        address= addressForm.address.data,
        city = addressForm.city.data,
        state=addressForm.state.data,
        zip_code=addressForm.zip_code.data,
        phone=addressForm.phone.data,
        user_id = current_user.id
    )
    db.session.add(new_address)
    db.session.commit()
    return new_address

def user_saved_shipping_addresses():
    addresses = ShippingAddress.query.filter_by(user_id=current_user.id)
    return addresses

@products_bp.route('/edit-shipping-address/<int:address_id>', methods=['GET', 'POST'])
@login_required
def edit_shipping_address(address_id):
    address = ShippingAddress.query.get_or_404(address_id)
    form = ShippingAddressForm(obj=address)

    if form.validate_on_submit():
        form.populate_obj(address)
        db.session.commit()
        flash(f"Shipping Address Edited Successfully!!!", 'success')
        return redirect(url_for('products_bp.chekout'))

    return render_template('products/edit_shipping_address.html', form=form)


# @products_bp.route('/delete-shipping-address/<int:address_id>', methods=['GET', 'POST'])
# @login_required
# def delete_shipping_address(address_id):
#     address = ShippingAddress.query.get_or_404(address_id)
#     db.session.delete(address)
#     db.session.commit()
#     return redirect(url_for('products_bp.chekout'))


@products_bp.route('/delete-shipping-address/<int:address_id>', methods=['GET', 'POST'])
@login_required
def delete_shipping_address(address_id):
    address = ShippingAddress.query.get_or_404(address_id)
    placed_orders_using_address = PlacedOrder.query.filter_by(shipping_address_id=address.id).count()
    
    if placed_orders_using_address > 0:
        flash('This address is being used in an order and cannot be deleted.', 'danger')
        return redirect(url_for('products_bp.chekout'))
    
    db.session.delete(address)
    db.session.commit()
    flash('Address deleted successfully.', 'success')
    return redirect(url_for('products_bp.chekout'))





@products_bp.route('/chekout', methods=['GET', 'POST'])
@login_required
def chekout():
    # Retrieve cart products
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if cart is None:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()

    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    cart_total = cart.get_cart_total_price() 

    #retrive saved shipping address
    user_addresses = user_saved_shipping_addresses()

    form = ShippingAddressForm()
    if form.validate_on_submit():
        address_obj = save_shipping_address(form)
        print(address_obj)
        flash('New address saved and proceeding to payment', 'success')

    if request.method == 'POST':
        selected_address_id = request.form.get('selected_address')
        
        if selected_address_id:
            session[f"{current_user.id}_selected_address_id"] = selected_address_id

            payment_methods = retrieve_stripe_saved_payment_methods_by_customer_id()
            if payment_methods:
                return redirect(url_for('payments_bp.saved_payment_methods'))
            else:
                return redirect(url_for('payments_bp.payment_info'))
        else:
            flash('Please Selsect a Shipping Address', 'info')

            # selected_address = ShippingAddress.query.get(selected_address_id)
            # if selected_address:
            #     placed_order = placed_order_from_cart_items(cart_items, selected_address, current_user)
            #     flash(f'Your Order Placed, Order Id {placed_order.order_id}', 'success')
            #     return redirect(url_for('home_bp.home'))


    return render_template('products/chekout.html', 
                           title='Checkout',
                           cart_items=cart_items,
                           cart_total=cart_total, 
                           form=form,
                           user_addresses=user_addresses
                           )