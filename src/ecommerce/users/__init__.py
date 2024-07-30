from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash
from ecommerce import admin, db
from .models import User
from flask import flash, Blueprint, url_for, request, redirect
from flask_login import current_user

class UserModelView(ModelView):
    column_exclude_list = ['password', ]
    form_excluded_columns = ['profile_pic','role','created_at' ]
    def create_model(self, form):
        try:
            model = self.model(
                username=form.username.data,
                email=form.email.data,
                password=generate_password_hash(form.password.data)
            )
            self.session.add(model)
            self._on_model_change(form, model, True)
            self.session.commit()
        except Exception as ex:
            self.session.rollback()
            flash('Failed to create record. %s' % str(ex), 'error')
            return False
        else:
            self.after_model_change(form, model, True)
        return model
    
    # def is_accessible(self):
    #     if not current_user.is_authenticated:
    #         return False
    #     if current_user.is_superadmin():
    #         return True
    #     return False

    # def inaccessible_callback(self, name, **kwargs):
    #     return redirect(url_for('user_bp.user_login', next=request.url))


# Add the custom model view to the admin
admin.add_view(UserModelView(User, db.session))