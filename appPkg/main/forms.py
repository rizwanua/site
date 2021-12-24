from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FloatField
from wtforms.validators import ValidationError, DataRequired, Length
from appPkg.models import Stock, User
from flask_table import Table, Col


class UserStocksTable(Table):
    symbol = Col('Stock')
    status = Col('Status')
    alertPrice  = Col('Alert Price')
    
class SelectStockForm(FlaskForm):
    submit = SubmitField('Add Stock Alert')

class DeleteStockForm(FlaskForm):
    submit = SubmitField('Delete Stock Alert')
    
class EnterPriceForm(FlaskForm):
    '''
    
    '''
    desiredPrice = FloatField('Enter Desired Price', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
class EditProfileForm(FlaskForm):
    '''
    TextAreaField - multi-line box in which the user can enter text. 
    To validate this field I'm using Length, which will make sure that the text entered is between 0 and 140 characters, which is the space I have allocated for the corresponding field in the database.
    '''
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About Me', validators = [Length(min=0, max=140)])
    submit = SubmitField('Submit')                            
    
    
    '''
    # Overloaded constructor accepts original username as argument
    # This is saved as an instance variable, and checked in validate_username
    # If the username entered in form is same as original username, no reason to check for duplicates
        
    super is used to invoke a method in the parent class. 
    In this particular case, I have created a class constructor and I want to invoke the class constructor in the parent class, which is the FlaskForm class. 
    Typically when you override a method in a derived class, you want to invoke the original method in the parent class as well.

    This is not a perfect solution, because it may not work when two or more processes are accessing the database at the same time. 
    In that situation, a race condition could cause the validation to pass, but a moment later when the rename is attempted the database was already changed by another process and cannot rename the user. 
    This is somewhat unlikely except for very busy applications that have a lot of server processes, so I'm not going to worry about it for now.
    
    The way to prevent the race conditions is by introducing locks, either at the database or application layers. 
    If you lock the users table between the time you check for the existance of the username until the time you use it, then you are guaranteed that the username will still be available when you use it.
    '''
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username = self.username.data).first()
            if user is not None:
                raise ValidationError('Username already exists. Please select a different username.')
                      
      