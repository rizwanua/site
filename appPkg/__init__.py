"""
Description:
    Main Initialization file for the Flask app
"""

import os
from config import Config

from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_apscheduler import APScheduler
from datetime import datetime, timedelta

import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

# Create Flask extension instances without attaching application
db = SQLAlchemy() 
migrate = Migrate()  
mail = Mail() 
bootstrap = Bootstrap() 
scheduler = APScheduler()

login = LoginManager()
login.login_view = 'auth.login' # Endpoint name
login.login_message = ('Please log in to access this page.')

from appPkg.main.handlers import checkAlerts # Placed here to avoid import error for DB
from appPkg.main.syslog import backup_logs
    
# Flask Application Factory 
def create_app(config_class=Config): 
    """
    Initialize the Flask app and extensions. 
    Initialize email handling for Python errors
    Initialize and startup the scheduler to check for alerts every X minutes.
    
    Parameters
    ----------
    config_class : Config
        Python app configuration data.

    Returns
    -------
    app : Instance of class Flask.
        Python app itself, Flask context

    """
    app = Flask (__name__) 
    app.config.from_object(Config) 

    # init_app() method invoked on extension instances to bind to the now known application. 
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    scheduler.init_app(app)
    
    # Register the errors blueprint with the application
    from appPkg.errors import bp as errors_bp 
    app.register_blueprint(errors_bp) 
    
    # Register the authentication blueprint with the application
    from appPkg.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Register the main blueprint with the application
    from appPkg.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    # Register the API blueprint with the application
    from appPkg.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Email Log Errors
    if not app.debug: # Only enable email logger when app in production mode
        if app.config['MAIL_SERVER']: 
            
            # Setup email handler
            auth=None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr=app.config['MAIL_USERNAME'],
                toaddrs=app.config['ADMINS'], subject='SPA Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
            
        # Logging exceptions that are not errors being emailed
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler('logs/spa.log', maxBytes=100000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
    
        app.logger.setLevel(logging.INFO)
        app.logger.info('SPA startup')
    
    # Start-up APScheduler to check alerts
    with app.app_context():
        
        # Initialize logTimeCheck to last year
        current_app.logTimeCheck = datetime.now() - timedelta(days=365)
        
        scheduler.add_job(func=checkAlerts, args=[current_app._get_current_object()], trigger='interval', id='job1', seconds=app.config['ALERT_CHECK_FREQUENCY'], timezone="UTC")
        scheduler.add_job(func=backup_logs, args=[current_app._get_current_object(), os.getcwd()], trigger='interval', id='job2', seconds=app.config['LOG_BACKUP_FREQUENCY'], timezone="UTC")
        scheduler.start()
        
    return app

from appPkg import models # At the end to prevent circular referencing