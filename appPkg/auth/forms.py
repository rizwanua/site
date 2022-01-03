"""
Description:
    User login/registration/password reset forms.
    
    Code modified as needed from https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from appPkg.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Re-enter Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """
        Validate if username input by user already exists in database.

        Parameters
        ----------
        username : string
            
        Raises
        ------
        ValidationError
            Error for user describing reason for username rejection

        Returns
        -------
        None.

        """
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already exists. Please use a different username')
    
    def validate_email(self, email):
        """
        Validate if email input by user already exists in database.

        Parameters
        ----------
        email : string

        Raises
        ------
        ValidationError
            Error for user describing reason for email rejection.

        Returns
        -------
        None.

        """
        user = User.query.filter_by (email = email.data).first()
        if user is not None:
            raise ValidationError('Email already exists. Please use a different email address.')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')