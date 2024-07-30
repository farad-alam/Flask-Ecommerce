from flask import Blueprint, render_template, jsonify, request, flash
import stripe
import json
import os
from dotenv import load_dotenv
from ecommerce.products.models import Cart, PlacedOrder, CartItem
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
def success():
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