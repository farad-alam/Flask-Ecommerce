from flask import Flask
from flask_login import LoginManager
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
import os
import sys
from flask_migrate import Migrate


app = Flask(__name__)


load_dotenv()

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['FLASK_ADMIN_SWATCH'] = 'darkly'



admin = Admin(app, name='E-commerce', template_mode='bootstrap3')

# Extensions
db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager(app)
csrf_token = CSRFProtect(app)
migrate = Migrate(app, db)


# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


from .home.routes import home_bp
from .users.routes import user_bp
from .products.routes import products_bp
from .payments.routes import payments_bp

# from .home.routes import home_bp
# from .users.routes import user_bp
# from .products.routes import products_bp
# from .payments.routes import payments_bp

app.register_blueprint(home_bp)
app.register_blueprint(user_bp)
app.register_blueprint(products_bp)
app.register_blueprint(payments_bp)

