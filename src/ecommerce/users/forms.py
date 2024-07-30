from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, SubmitField, EmailField, PasswordField, FileField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length, Email, ValidationError
from .models import User
from flask_login import current_user

class UserRegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=20)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    image = FileField('Profile Image (Optional)', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(f"This username '{username.data}' is already taken, please choose different one!")
        
    def validate_email(self, email):
        user = User.query.filter_by(username=email.data).first()
        if user:
            raise ValidationError(f"This email '{email.data}' is already taken, please choose different one!")
        
class UserLoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')




class User_Account_Update_Form(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    image = FileField('Profile Image (Optional)', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user and user.username != current_user.username:
            raise ValidationError(f"This username '{username.data}' is already taken, please choose different one!")
        
    def validate_email(self, email):
        user = User.query.filter_by(username=email.data).first()
        if user and user.email != current_user.email:
            raise ValidationError(f"This email '{email.data}' is already taken, please choose different one!")

class Request_Password_Reset_Form(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Pssword Reset')

class Password_Reset_Form(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

