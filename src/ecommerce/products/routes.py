from flask import Blueprint



products_bp = Blueprint('products_bp', __name__, url_prefix='/product')

@products_bp.route('/products')
def products():
    return "this is products"