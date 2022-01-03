"""
Description:
    Send password reset email to user.
    
    Code modified as needed from https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
"""

from flask import render_template, current_app
from appPkg.email import send_email


def send_password_reset_email(user):
    """
    Setup parameters for send_email

    Parameters
    ----------
    user : User instance
        
    Returns
    -------
    None.

    """
    token = user.get_reset_password_token()
    send_email('[StockPriceAlert] Reset Your Password',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))