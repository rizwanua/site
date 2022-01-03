"""
Description:
    Routes for user authentication - login/registration/password reset.
    
    Code modified as needed from https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from werkzeug.urls import url_parse
from appPkg.auth.email import send_password_reset_email
from appPkg import db
from appPkg.auth import bp
from appPkg.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from appPkg.models import User
from appPkg.main.syslog import logInfo

@bp.route('/login', methods=['GET', 'POST']) # Default is GET only
def login():
    """
    Route for Login page

    Returns
    -------
    HTML template
    Redirect webpage
    """
    
    if current_user.is_authenticated: # Dont want a logged in user to go to the login page again
        logInfo(f'Login as user {current_user.id}') # Log client information
        return redirect(url_for('main.index')) 
    else:
        logInfo(f'Login as anonymous') # Log client information

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first() # Load user from database
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember = form.remember_me.data) # function will register the user as logged in, so that means that any future pages the user navigates to will have the current_user variable set to that user
        
        '''
        # Following text is from miguelgrinberg.com:
            
        request.args attribute exposes the contents of the query string in a dictionary format. 
        Three possible cases to be considered to determine where to redirect after a successful login:

        1) If the login URL does not have a next argument, then the user is redirected to the index page.
        
        2) If the login URL includes a next argument that is set to a relative path then the user is redirected to that URL.
        
        3) If the login URL includes a next argument that is set to a full URL that includes a domain name, then the user is redirected to the index page.
        The third case is in place to make the application more secure to prevent an attacker from inserting a URL to a malicious website.
        To determine if the URL is relative or absolute, parse it with Werkzeug's url_parse() function and then check if the netloc component is set or not.
        
        '''
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(url_for('main.index')) 
        
    return render_template('auth/login.html', title='Sign In Page', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Route for Registration
    Create a new user with the username, email and password provided

    Returns
    -------
    HTML template
    Redirect webpage
    """
   
    if current_user.is_authenticated:
        logInfo(f'Register as user {current_user.id}') # Log client information
        return redirect(url_for('index')) # Redirect: Go to index page
    else:
        logInfo(f'Register as anonymous') # Log client information
        
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now registered!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Registration Form', form=form)


@bp.route('/logout')
def logout():
    """
    Logout user

    Returns
    -------
    Redirect webpage
    """
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """
    Allows the user to reset their password to their email address.

    Returns
    -------
    HTML template
    Redirect webpage        
    """
    if current_user.is_authenticated:
        logInfo(f'Initiate reset password as user {current_user.id}') # Log client information
        return redirect(url_for('main.index'))
    else:
        logInfo(f'Initiate reset password as anonymous') # Log client information
        
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('If the account is valid, check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Triggered AFTER the user clicks the reset URL in their email

    Parameters
    ----------
    token : string
        Token to reset user password

    Returns
    -------
    HTML template
    Redirect webpage
    """
    if current_user.is_authenticated:
        logInfo(f'Reset password as user {current_user.id}') # Log client information
        return redirect(url_for('main.index'))
    else:
        logInfo(f'Reset password anonymous') # Log client information
        
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

