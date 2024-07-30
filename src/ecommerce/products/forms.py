from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class ShippingAddressForm(FlaskForm):
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    zip_code = IntegerField('Zip Code', validators=[DataRequired()])
    phone = IntegerField('Phone Number', validators=[DataRequired()])
    submit = SubmitField('Add Address')

