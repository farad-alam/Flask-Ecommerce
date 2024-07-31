from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
import stripe
import json
import os
from dotenv import load_dotenv
from ecommerce.products.models import Cart, CartItem
from flask_login import current_user, login_required
from sqlalchemy.orm import lazyload

load_dotenv()

payments_bp = Blueprint('payments_bp', __name__, url_prefix='/payments')

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


@payments_bp.route('/payment-info')
def payment_info():
    return render_template('payments/payment_info.html', title="Payment Info")



@payments_bp.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    try:

        intent = stripe.PaymentIntent.create(
            amount=5600,
            currency='usd',
            # customer='cus_ID',
            automatic_payment_methods={
                    'enabled': True,
                },
        )

        return jsonify({
            'clientSecret': intent['client_secret']
        })
    
    except Exception as e:
        return jsonify(
            error = str(e)
        ), 403


def get_cart_details_by_user():
    current_user_cart = Cart.query.filter_by(user_id=current_user.id).first()
    user_cart_items = CartItem.query.filter_by(cart_id=current_user_cart.id).options(lazyload('*'))
    return user_cart_items

@payments_bp.route('/success')
@login_required
def payment_success():
    # client_secret = request.args.get("payment_intent_client_secret")
    try:
        intent_id = request.args.get("payment_intent")

        # retrieve the intent
        payment_intent_obj = stripe.PaymentIntent.retrieve(intent_id)
        amount_received = payment_intent_obj['amount_received'] / 100

        #Update The Intent
        cart_items = get_cart_details_by_user()
        serialized_user_cart_items = json.dumps([item.to_dict() for item in cart_items])
        print(serialized_user_cart_items)
        payment_intent_obj = stripe.PaymentIntent.modify(
            intent_id,
            metadata= {'products': serialized_user_cart_items},
        )
        return render_template('payments/success.html', 
                               title="Payment Success", 
                               amount_received=amount_received,
                               cart_items = cart_items,
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
def setup_complete():
    intent_id = request.args.get("setup_intent")
    
    return render_template('payments/setup_complete.html',
                            title="Setup Complete",
                            intent_id=intent_id
                            )

# @payments_bp.route('/test')
def retrieve_stripe_saved_payment_methods_by_customer_id(customer_id):
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


@payments_bp.route('/saved-payment-methods')
@login_required
def saved_payment_methods():
    stripe_cus_id = retrive_or_create_stripe_customer_id()
    payment_methods = retrieve_stripe_saved_payment_methods_by_customer_id(stripe_cus_id)
    
    if payment_methods is None:
        return redirect(url_for('payments_bp.payment_info'))
    else:
        return render_template('payments/saved_payment_methods.html', payment_methods=payment_methods )


@payments_bp.route('/pay-with-existing-card/<cus_id>/<pm_id>')
def pay_with_existing_card(cus_id, pm_id):
    print(cus_id,pm_id, sep='|')
    try:
       payment = stripe.PaymentIntent.create(
            amount=1099,
            currency='usd',
            # In the latest version of the API, specifying the `automatic_payment_methods` parameter is optional because Stripe enables its functionality by default.
            automatic_payment_methods={"enabled": True},
            customer=cus_id,
            payment_method=pm_id,
            # return_url= url_for('payments_bp.payment_success',_external=True),
            return_url='http://127.0.0.1:5000/payments/success',
            off_session=True,
            confirm=True,
        )
       print(payment)
       return redirect(url_for('payments_bp.payment_success',payment_intent=payment['id']))
    except stripe.error.CardError as e:
        err = e.error
        # Error code will be authentication_required if authentication is needed
        print("Code is: %s" % err.code)
        # payment_intent_id = err.payment_intent['id']
        # payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        # print('error intent------------------------', payment_intent)
        # return None
        flash('an error occured when proccessing payments', 'info')
        return redirect(url_for('payments_bp.saved_payment_methods'))