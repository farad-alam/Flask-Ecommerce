from flask_admin.contrib.sqla import ModelView
from ecommerce import admin, db
from .models import Categories, Products
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_admin.form import ImageUploadField

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
        'image': ImageUploadField('Image', base_path='static/product/images')
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



# Add the custom model view to the admin
admin.add_view(CategoriesModelView(Categories, db.session))
admin.add_view(ProductsModelView(Products, db.session))