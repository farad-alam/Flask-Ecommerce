from flask import Blueprint, render_template
from ecommerce.products.models import Products


home_bp = Blueprint('home_bp',__name__)


@home_bp.route('/')
def home():
    products = Products.query.all()
    return render_template('home/home.html',products=products, title='Home - Ecommerce')