from flask import Blueprint, render_template, request
from ecommerce.products.models import Products, PlacedOrder
from ecommerce import db
from flask_login import login_required, current_user

home_bp = Blueprint('home_bp',__name__)


@home_bp.route('/')
def home():
    products = Products.query.all()
    return render_template('home/home.html',products=products, title='Home - Ecommerce')

@home_bp.route('/user-dashboard')
@login_required
def user_dashboard():
    placed_oders = PlacedOrder.query.filter_by(user_id=current_user.id)

    

    return render_template('home/user_dashboard.html',
                           title='Dashboard',
                           placed_oders=placed_oders,
                           
                           )


@home_bp.route('/search-product/', methods=['GET'])
def search_product():
    query = request.args.get('query')
    if query:
        results = Products.query.filter(Products.title.ilike(f'%{query}%')).all()
    else:
        results = []

    return render_template('home/search_results.html', query=query, results=results)
