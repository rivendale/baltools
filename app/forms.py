from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class AddressForm(FlaskForm):
    ethaddress = StringField('ETH Address', validators=[DataRequired()])
    submit = SubmitField('Sign In')

