from ecommerce import db
from flask_login import UserMixin
from sqlalchemy import event
from slugify import slugify
from datetime import datetime
import os
from PIL import Image
from flask import url_for, current_app
from werkzeug.utils import secure_filename
import uuid
from werkzeug.datastructures import FileStorage


# CATEGORIES MODEL ------------------>>>

# A function to generate a slug from the name
def generate_slug(mapper, connection, target):
    if target.name:
        target.slug = slugify(target.name)


class Categories(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    slug = db.Column(db.String(35), nullable=False, unique=True)

# Attach the event listener to the Categories model
event.listen(Categories, 'before_insert', generate_slug)
event.listen(Categories, 'before_update', generate_slug)



# PRODUCT MODEL ------------->>>

class Products(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    product_desc = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(250), nullable=True)  # Assuming storing image URL/path
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship('Categories', backref=db.backref('products', lazy=True))
    slug = db.Column(db.String(255), nullable=False, unique=True)
    created_at =  db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def save_image(self, image_file):

        if isinstance(image_file, FileStorage) and image_file.filename != '':
            # Ensure the directory exists
            directory = os.path.join(current_app.root_path, 'static/product/images')
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Generate a unique filename with UUID and file extension
            filename = secure_filename(image_file.filename)
            file_ext = os.path.splitext(filename)[1]
            unique_filename = str(uuid.uuid4()) + file_ext
            filepath = os.path.join(directory, unique_filename)

            # Compress and save the image
            output_size = (300, 300)
            img = Image.open(image_file)
            img.thumbnail(output_size)
            img.save(filepath, optimize=True, quality=85)
            self.image = url_for('static', filename='product/images/' + unique_filename)
        elif isinstance(image_file, str) and image_file:  # When editing, keep the existing image
            self.image = image_file
        else:
            self.image = url_for('static', filename='product/images/default-product-img.jpg')

# A function to generate a slug from the title
def generate_product_slug(mapper, connection, target):
    if target.title:
        target.slug = slugify(target.title)

# Attach the event listener to the Products model
event.listen(Products, 'before_insert', generate_product_slug)
event.listen(Products, 'before_update', generate_product_slug)




# CART MODELS ---------------------->>>

class CartItem(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product = db.relationship('Products', backref=db.backref('cart_items', lazy=True))
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.now)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)

    def get_cart_item_total_price(self):
        return self.quantity * self.product.price

class Cart(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  
    user = db.relationship('User', backref=db.backref('cart', lazy=True))
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade="all, delete-orphan")
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def get_cart_total_price(self):
        return sum(item.product.price * item.quantity for item in self.items)

    




