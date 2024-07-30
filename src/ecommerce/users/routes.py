from .models import User
from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint
from ecommerce import db, mail
from .forms import UserRegistrationForm, UserLoginForm, User_Account_Update_Form, Request_Password_Reset_Form, Password_Reset_Form
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import current_user, login_user, logout_user, login_required
from PIL import Image
import os, secrets
from flask_mail import Message
# from ecommerce.users import user_bp


user_bp = Blueprint("user_bp", __name__, url_prefix='/user')

@user_bp.route('/register', methods=['GET','POST'])
def user_register():

    if current_user.is_authenticated:
        return redirect(url_for("home_bp.home"))
    
    form = UserRegistrationForm()
    if form.validate_on_submit():

        hex_password = generate_password_hash(form.password.data)
        new_user = User(
            first_name=form.first_name.data,
            last_name = form.last_name.data,
            username=form.username.data,
            email=form.email.data,
            password=hex_password,
        )

        db.session.add(new_user)
        db.session.commit()
        # Send a success email to newuser
        send_mail(
            f"{new_user.first_name}, Your have successfully created account on Flask Ecommerce!!!",
            [new_user.email],
            f''' Hi {new_user.first_name},
Your have successfully created accoun on Flask Ecommerce!!!

Take a tour on our site to explore more new things


Regards
Farad Alam
Senior Dev at flask-ecommerce
'''

        )
        flash(f'Your Account Successfully Created {form.username.data} !!!', 'success')
        return redirect(url_for('user_bp.user_login'))

    return render_template('users/register.html', form=form, title="Sign Up")


@user_bp.route('/login', methods=['GET','POST'])
def user_login():

    if current_user.is_authenticated:
        return redirect(url_for("home_bp.home"))
    
    form = UserLoginForm()
    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash(f"Welcome {user.username} !!!, You have successfully logged in", 'success')
            return redirect(next_page) if next_page else redirect(url_for('home_bp.home'))
        else:
            flash("Plese Enter Correct email or password !", 'warning')
        
    return render_template('users/login.html', form=form, title='Login')
    

@user_bp.route('/logout', methods=['GET'])
def user_logout():
    logout_user()
    return redirect(url_for('user_bp.user_login'))

@user_bp.route('/account')
@login_required
def user_account():
    return render_template('users/account.html', title='Account', current_user=current_user)






def save_profile_image(image_data):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(image_data.filename)
    filename = secure_filename(f"{random_hex}{f_ext}")
    filepath = os.path.join(current_app.root_path, 'static/profile_pics')

    # Ensure the directory exists
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    full_filepath = os.path.join(filepath, filename)

    # Resize and save the image
    output_size = (100, 100)
    image = Image.open(image_data)
    image.thumbnail(output_size)
    image.save(full_filepath)

    return filename


@user_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_account_edit(user_id):
    user = User.query.get_or_404(user_id)
    if user != current_user:
        flash('You can only edit your own account!', 'danger')
        return redirect(url_for('home_bp.home'))
    
    form = User_Account_Update_Form()

    if form.validate_on_submit():
        if form.username.data != user.username:
            user.username = form.username.data
        if form.email.data != user.email:
            user.email = form.email.data
        
        if form.image.data:
            # Save the profile image
            image_file = save_profile_image(form.image.data)
            user.profile_pic = image_file
        
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('user_bp.user_account', user_id=user.id))
    
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
    
    return render_template('users/account_edit.html', title='Account Edit', form=form)


def send_password_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        'Reset Your Password',
        sender='flask-ecommerce@gmail.com',
        recipients=[user.email]
    )
    msg.body = f'''To Reset you password, click on the following link:
    {url_for('user_bp.password_reset', token=token, _external=True)}
    if your are not request for password, then ignore this message, no change will happen on your account

'''
    mail.send(msg)

def send_mail(subject, recipients:list, msg_body, sender='flask-ecommerce@gmail.com'):
    msg = Message(
        f'{subject}',
        sender=sender,
        recipients= recipients
    )
    msg.body = msg_body
    mail.send(msg)



# Use .environ to hise sercrate 

@user_bp.route('/request-password-reset', methods=['GET', 'POST'])
def request_password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('home_bp.home'))
    form = Request_Password_Reset_Form()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('The email you enter have no account!!!', 'info')
            return redirect(url_for('user_bp.user_register'))
        send_password_reset_email(user)
        flash('An email send to your email with password reset instruction', 'info')
        return redirect(url_for('user_bp.user_login'))
    return render_template('users/request_password_reset.html', form=form)


@user_bp.route('/password-reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    # authenticat the user
    if current_user.is_authenticated:
        return redirect(url_for('home_bp.home'))
    
    # verify the token and chek user existence
    user = User.verify_reset_token(token,300)
    if user is None:
        flash('The Request is Invalid or token Expaired','warning')
        return redirect(url_for('user_bp.request_password_reset'))
    
    #validate the form data and save the new password
    form = Password_Reset_Form()
    if form.validate_on_submit():
        hex_password = generate_password_hash(form.password.data)
        user.password=hex_password
        db.session.commit()

        # Send a success email to recipents
        send_mail(
            f"{user.username}, Your password reset successfully!!!",
            [user.email],
            f''' Hi {user.username},
Your Password Successfully Reset.

If you have not reset the password, then contact our support: contact@flask-ecommerce.com


Regards
Farad Alam
Senior Dev at flask-ecommerce
'''

        )
        flash(f'Your Password Successfully Reset !!!', 'success')
        return redirect(url_for('user_bp.user_login'))

    return render_template('users/password_reset.html', form=form)