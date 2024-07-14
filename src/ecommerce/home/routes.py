from flask import Blueprint, render_template
from ecommerce.products.models import Products
from flask_login import login_required, current_user
from ecommerce.products.models import PlacedOrder, PlacedOrderItem

home_bp = Blueprint('home_bp',__name__)


@home_bp.route('/')
def home():
    products = Products.query.all()
    return render_template('home/home.html',products=products, title='Home - Ecommerce')

@home_bp.route('/user-dashboard')
@login_required
def user_dashboard():
    placed_oders = PlacedOrder.query.filter_by(user_id=current_user.id)
    total_price = sum([oder_items.oder_item_price for order in placed_oders  for oder_items in order.items ])

    return render_template('home/user_dashboard.html',
                           title='Dashboard',
                           placed_oders=placed_oders,
                           total_price = total_price
                           )