"""
Description:
    Flask-forms to allow user to enter the desired alert price, as well as Submit buttons.
"""

from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FloatField
from wtforms.validators import ValidationError, DataRequired, Length
from appPkg.models import Stock, User

    
class SelectStockForm(FlaskForm):
    """
    Used in "manage_alerts"
    """
    submit = SubmitField('Add Stock Alert')

class DeleteStockForm(FlaskForm):
    """
    Used in "manage_alerts"
    """
    submit = SubmitField('Delete Stock Alert')
    
class EnterPriceForm(FlaskForm):
    """
    Used in "enter_price"
    """
    desiredPrice = FloatField('Enter Desired Alert Price', validators=[DataRequired(message = 'Please enter numerical integers and "." only.')])
    submit = SubmitField('Submit')
