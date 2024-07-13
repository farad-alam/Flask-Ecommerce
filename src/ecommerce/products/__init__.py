from flask_admin.contrib.sqla import ModelView
from ecommerce import admin, db
from .models import Categories, Products, CartItem, Cart
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_admin.form import ImageUploadField
from ecommerce.users.models import User
from flask_login import current_user

class CategoriesModelView(ModelView):
    form_excluded_columns = ['slug',]

class ProductsModelView(ModelView):
    form_excluded_columns = ['slug',]
    column_exclude_list = ['product_desc', ]

    # This will be called to generate a list of categories
    def category_query():
        return Categories.query

    # Add a QuerySelectField to the form for categories
    form_extra_fields = {
        'category': QuerySelectField('Category', query_factory=category_query, allow_blank=False, get_label='name'),
        'image': ImageUploadField('Image', base_path='ecommerce/static/product/images')
    }

    # To exclude 'category_id' from the form (since we use 'category' instead)
    form_columns = ['title', 'product_desc', 'image', 'price', 'category']

    def create_model(self, form):
        model = self.model()
        form.populate_obj(model)
        model.save_image(form.image.data)
        self.session.add(model)
        self.session.commit()
        return model

    def update_model(self, form, model):
        form.populate_obj(model)
        model.save_image(form.image.data)
        self.session.commit()
        return model



class CartModelView(ModelView):
    form_excluded_columns = ['created_at','updated_at','items']
        
    # This will be called to generate a list of user
    def user_query():
        return User.query
    
    # This will be called to generate a list of user
    def cartitem_query():
        return CartItem.query
    
     # Add a QuerySelectField to the form 
    form_extra_fields = {
        'user': QuerySelectField('User', query_factory=user_query, allow_blank=False, get_label='username'),
        'items': QuerySelectField('CartItem', query_factory=cartitem_query, allow_blank=True, get_label='product.title')
    }

    # FOr Cart odel
    def create_model(self, form):
        model = self.model()
        form.populate_obj(model)
        self.session.add(model)
        self.session.commit()
        return model

    def update_model(self, form, model):
        form.populate_obj(model)
        self.session.commit()
        return model



class CartItemModelView(ModelView):
    form_excluded_columns = ['created_at',]

    # This will be called to generate a list of product
    def product_query():
        return Products.query
    
    def cart_query():
        return Cart.query
    
        # Add a QuerySelectField to the form 
    form_extra_fields = {
        'product': QuerySelectField('Product', query_factory=product_query, allow_blank=False, get_label='title'),
        'cart': QuerySelectField('Cart', query_factory=cart_query, allow_blank=False, get_label='id')
    }

    # For CartItem
    def create_model(self, form):
        model = self.model()
        form.populate_obj(model)
        self.session.add(model)
        self.session.commit()
        return model

    def update_model(self, form, model):
        form.populate_obj(model)
        self.session.commit()
        return model


# Add the custom model view to the admin
admin.add_view(CategoriesModelView(Categories, db.session))
admin.add_view(ProductsModelView(Products, db.session))
admin.add_view(CartItemModelView(CartItem, db.session))
admin.add_view(CartModelView(Cart, db.session))