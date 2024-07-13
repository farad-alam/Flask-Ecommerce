from flask import Blueprint, render_template, redirect, url_for
from .models import Products

products_bp = Blueprint('products_bp', __name__, url_prefix='/product')

@products_bp.route('/products')
def products():
    return "this is products"

@products_bp.route('/product-details/<slug>')
def product_details(slug):
    product = Products.query.filter_by(slug=slug).first()
    return render_template('products/product_details.html', product=product, title=f'{product.title}')