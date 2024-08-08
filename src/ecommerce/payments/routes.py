from flask import (Blueprint,render_template, jsonify, request, 
                   flash, redirect, url_for, session)
from ecommerce.products.models import Cart, CartItem, PlacedOrder, PlacedOrderItem
from ecommerce import db
from flask_login import current_user, login_required
from sqlalchemy.orm import lazyload
from dotenv import load_dotenv
import stripe
import json
import os



load_dotenv()

payments_bp = Blueprint('payments_bp', __name__, url_prefix='/payments')

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


@payments_bp.route('/payment-info')
@login_required
def payment_info():
    cart_items = get_cart_details_by_user()
    return render_template('payments/payment_info.html', 
                           title="Payment Info",
                           cart_items = cart_items,
                           )



@payments_bp.route('/create-payment-intent', methods=['POST'])
@login_required
def create_payment_intent():
    try:
        cart_items = get_cart_details_by_user()
        if cart_items:
            user_cart_total_price = cart_items[0].cart.get_cart_total_price()
            print(int(user_cart_total_price*100))
            intent = stripe.PaymentIntent.create(
                amount=int(user_cart_total_price*100),
                currency='usd',
                customer= retrive_or_create_stripe_customer_id(),
                automatic_payment_methods={
                        'enabled': True,
                    },
                setup_future_usage = 'off_session',
            )
            print(intent)

            return jsonify({
                'clientSecret': intent['client_secret']
            })
        else:
            flash('You dont have a products in your car, first add product to cart', 'info')
            return redirect(url_for('home_bp.home'))
    
    except Exception as e:
        print(e)
        return jsonify(
            error = str(e)
        ), 403


def get_cart_details_by_user(types='list'):
    current_user_cart = Cart.query.filter_by(user_id=current_user.id).first()
    # user_cart_items = CartItem.query.filter_by(cart_id=current_user_cart.id).options(lazyload('*')).all()
    user_cart_items = CartItem.query.filter_by(cart_id=current_user_cart.id).options(lazyload('*'))
    print('on the get Cart func-------------------------------',user_cart_items)

    if user_cart_items is None or (isinstance(user_cart_items, list) or not user_cart_items):
        return redirect(url_for('products_bp.user_cart'))

    if types == 'json':
        serialized_user_cart_items = json.dumps([item.to_dict() for item in user_cart_items])
        print(serialized_user_cart_items)
        return serialized_user_cart_items
    elif types == 'list':
        return user_cart_items

@payments_bp.route('/success')
@login_required
def payment_success():
    # client_secret = request.args.get("payment_intent_client_secret")
    try:
        intent_id = request.args.get("payment_intent")
        cart_items = get_cart_details_by_user()
        print('Cart Items---------->>>', cart_items)

        if cart_items is None or (isinstance(cart_items, list) and not cart_items):
            return redirect(url_for('home_bp.user_cart'))
        # retrieve the intent
        payment_intent_obj = stripe.PaymentIntent.retrieve(intent_id)
        print(payment_intent_obj)

        amount_received = payment_intent_obj['amount_received'] / 100

        #Update The Intent
        serialized_user_cart_items = json.dumps([item.to_dict() for item in cart_items])
        print('Serilizes-------------->>>>>>', serialized_user_cart_items)
        
        payment_intent_obj = stripe.PaymentIntent.modify(
            intent_id,
            metadata= {'products': serialized_user_cart_items},
        )

        # if payment was succed placed ot order
        if payment_intent_obj['status'] == 'succeeded':
            selected_address_id = session[f"{current_user.id}_selected_address_id"]

            placed_order_items = placed_order_from_cart_items(
                cart_items=cart_items,
                shipping_address_id=selected_address_id,
                user=current_user,
            )
            print(placed_order_items)
        return render_template('payments/success.html', 
                               title="Payment Success", 
                               amount_received=amount_received,
                               placed_order_items = placed_order_items,
                               )
    except Exception as e:
        print(e)
        # cart_items = json.dumps(cart_items)
        flash("You are sending invalid request, please make a payment first",'info')
        return render_template('payments/success.html', title="Payment Success", amount_received="Invalid Request")


# @payments_bp.route('/test')
def retrive_or_create_stripe_customer_id(user_obj=current_user):

    try:
        user = stripe.Customer.search(query=f"email:'{user_obj.email}'")
        if user['data']:
            print('EXISTING USER ID --->>> ',user['data'][0]['id'])
            return user['data'][0]['id']
    except Exception as e:
        print(e)
        return None
    
    else:
        user = stripe.Customer.create(
            name=current_user.first_name,
            email=current_user.email
        )

        # LATER ADD THE STRIPE CUS_ID TO THE BUISNESS USER MODEL
        print('NEW USER iS --->>>', user['id'])
        return user['id']


# setupIntent for SAVING PAYMENT METHOD FOR FUTURE USASES -------->>>>


@payments_bp.route('/create-setup-intent', methods=['POST'])
@login_required
def create_setupIntent():
    # CREATE A SETUPINTENT AND SEND THE setupnIntent.client_secret to the CLIENT SIDE
    try:
        setup_intent = stripe.SetupIntent.create(
            customer=retrive_or_create_stripe_customer_id(),
            automatic_payment_methods = {
                'enabled':True
            }
        )
        return jsonify(clientSecret = setup_intent.client_secret)
    
    except Exception as e:
        return jsonify(error = str(e))


@payments_bp.route('/save-payment-details')
@login_required
def save_payment_details():
    
    return render_template('payments/setup_intent.html', title='Save Your Payment Details for Feature Use')


@payments_bp.route('/setup-complete')
@login_required
def setup_complete():
    intent_id = request.args.get("setup_intent")
    
    return render_template('payments/setup_complete.html',
                            title="Setup Complete",
                            intent_id=intent_id
                            )

# @payments_bp.route('/test')
def retrieve_stripe_saved_payment_methods_by_customer_id(customer_id=None):

    if customer_id:
        customer_id = customer_id
    elif customer_id == None:
        # get the current loged in user stripe customer id
        customer_id = retrive_or_create_stripe_customer_id()
    
    payment_methods_list = stripe.PaymentMethod.list(
        customer=customer_id,
        type="card"
    )
    if payment_methods_list['data']:
       print(payment_methods_list['data'])
       return payment_methods_list['data']
    else:
        return None
    # return render_template('test.html', data=payment_methods_list)



def placed_order_from_cart_items(cart_items, shipping_address_id, user):

    if cart_items is None:
        flash('your cart had no products', 'info')
        return redirect(url_for('products_bp.chekout'))
    
    new_placed_order = PlacedOrder(
        user_id = user.id,
        user = user,
        shipping_address_id = shipping_address_id
    )
    db.session.add(new_placed_order)

    print(cart_items)

    for items in cart_items:
        new_placed_order_item = PlacedOrderItem(
            order_id = new_placed_order.id,
            order = new_placed_order,
            product_id = items.product_id,
            product = items.product,
            quantity = items.quantity,
            oder_item_price = items.get_cart_item_total_price()
        )
        db.session.add(new_placed_order_item)
        db.session.delete(items)

    print('Olaced order woek succesfully.........................')
    db.session.commit()

    new_placed_order_items = PlacedOrderItem.query.filter_by(order_id=new_placed_order.id)
    
    return new_placed_order_items


@payments_bp.route('/saved-payment-methods')
@login_required
def saved_payment_methods():
    # stripe_cus_id = retrive_or_create_stripe_customer_id()
    payment_methods = retrieve_stripe_saved_payment_methods_by_customer_id()
    
    if payment_methods is None:
        return redirect(url_for('payments_bp.payment_info'))
    else:
        return render_template('payments/saved_payment_methods.html', payment_methods=payment_methods )


@payments_bp.route('/pay-with-existing-card/<cus_id>/<pm_id>')
@login_required
def pay_with_existing_card(cus_id, pm_id):
    print(cus_id,pm_id, sep='|')
    try:
        cart_items = get_cart_details_by_user()

        if cart_items:
            serialized_user_cart_items = json.dumps([item.to_dict() for item in cart_items])
            user_cart_total_price = int(cart_items[0].cart.get_cart_total_price()*100)
            print(user_cart_total_price)
            payment = stripe.PaymentIntent.create(
                    amount=user_cart_total_price,
                    currency='usd',
                    # In the latest version of the API, specifying the `automatic_payment_methods` parameter is optional because Stripe enables its functionality by default.
                    automatic_payment_methods={"enabled": True},
                    customer=cus_id,
                    payment_method=pm_id,
                    # metadata = {'products': serialized_user_cart_items},
                    # return_url= url_for('payments_bp.payment_success',_external=True),
                    return_url='http://127.0.0.1:5000/payments/success',
                    off_session=True,
                    confirm=True,
                )
            print(payment)
            return redirect(url_for('payments_bp.payment_success',payment_intent=payment['id']))
        else:
            flash('You dont have a products in your car, first add product to cart', 'info')
            return redirect(url_for('home_bp.home'))
    except stripe.error.CardError as e:
        err = e.error
        # Error code will be authentication_required if authentication is needed
        print("Code is: %s" % err.code)
        # payment_intent_id = err.payment_intent['id']
        # payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        # print('error intent------------------------', payment_intent)
        # return None
        flash('an error occured when proccessing payment methods', 'info')
        return redirect(url_for('payments_bp.saved_payment_methods'))