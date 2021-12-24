from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from appPkg.auth.email import send_password_reset_email
from appPkg import db
from appPkg.auth import bp
from appPkg.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from appPkg.models import User


'''
When defining routes in a blueprint, the @bp.route decorate is used instead of @app.route.

There is also a required change in the syntax used in the url_for() to build URLs
For regular view functions attached directly to the application, the first argument to url_for() is the view function name. 
When a route is defined in a blueprint, this argument must include the blueprint name and the view function name, separated by a period.
So for example, I had to replace all occurrences of url_for('login') with url_for('auth.login'), and same for the remaining view functions.
'''

@bp.route('/login', methods=['GET', 'POST']) # Default is GET only
def login():
    if current_user.is_authenticated: # Dont want logged in user to go to the login page again
        return redirect(url_for('main.index')) # Redirect: Go to another webpage

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first() # Load user from database
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember = form.remember_me.data) # function will register the user as logged in, so that means that any future pages the user navigates to will have the current_user variable set to that user
        
        '''
        Right after the user is logged in by calling Flask-Login's login_user() function, the value of the next query string argument is obtained. 
        Flask provides a request variable that contains all the information that the client sent with the request. 
        In particular, the request.args attribute exposes the contents of the query string in a friendly dictionary format. 
        There are actually three possible cases that need to be considered to determine where to redirect after a successful login:

        1) If the login URL does not have a next argument, then the user is redirected to the index page.
        
        2) If the login URL includes a next argument that is set to a relative path (or in other words, a URL without the domain portion), then the user is redirected to that URL.
        
        3) If the login URL includes a next argument that is set to a full URL that includes a domain name, then the user is redirected to the index page.
        The third case is in place to make the application more secure. 
        An attacker could insert a URL to a malicious site in the next argument, so the application only redirects when the URL is relative, which ensures that the redirect stays within the same site as the application. 
        To determine if the URL is relative or absolute, I parse it with Werkzeug's url_parse() function and then check if the netloc component is set or not.
        
        '''
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(url_for('main.index')) # Redirect: Go to index page
        
    return render_template('auth/login.html', title='Sign In Page', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index')) # Redirect: Go to index page
    
    '''
    Creates a new user with the username, email and password provided
    Write to the database, and then redirects to the login prompt so that the user can log in.
    '''
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
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
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

