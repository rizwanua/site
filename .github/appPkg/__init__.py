from flask import Flask, request, current_app 
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask_mail import Mail

db = SQLAlchemy() # Database - flask_sqlalchemy - Object represents the database
migrate = Migrate()  # Database - flask_migrate
mail = Mail() # Flask-Mail instance
bootstrap = Bootstrap() # Flask-Bootstrap instance

# Flask_login
login = LoginManager()
login.login_view = 'auth.login' #endpoint name
login.login_message = ('Please log in to access this page.')

# Application Factory Pattern
def create_app(config_class=Config): 
    app = Flask (__name__) 
    app.config.from_object(Config) 
 
    # At the time the application instance is created in the factory function here,  
    # the init_app() method must be invoked on the extension instances to bind it to the now known application. 
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    
    # Register the errors blueprint with the application
    from appPkg.errors import bp as errors_bp # Import here to avoid circular dependencies
    app.register_blueprint(errors_bp) # When a blueprint is registered, any view functions, templates, static files, error handlers, etc. are connected to the application
    
    # Register the authentication blueprint with the application
    from appPkg.auth import bp as auth_bp
    '''
    url_prefix is optional. Any routes defined in the blueprint get this prefix in their URLs
    Useful as a sort of "namespacing" that keeps all the routes in the blueprint separated from other routes in the application or other blueprints
    So now the login URL is going to be http://localhost:5000/auth/login
    '''
    app.register_blueprint(auth_bp, url_prefix='/auth') 
    
    # Register the main blueprint with the application
    from appPkg.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    # Email Log Errors
    # not app.testing clause to the conditional that decides if email and file logging should be enabled or not, so that all this logging is skipped during unit tests.
    if not app.debug and not app.testing: # Only enable email logger when app in production mode
        if app.config['MAIL_SERVER']: # Only email when email server exists in config
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
        '''
        RotatingFileHandler class is nice because it rotates the logs, ensuring that the log files do not grow too large when the application runs for a long time. 
        In this case I'm limiting the size of the log file to 10KB, and I'm keeping the last ten log files as backup
        '''

        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler('logs/spa.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
    
        app.logger.setLevel(logging.INFO)
        app.logger.info('SPA startup')
        
    return app

from appPkg import models # Models module will define the structure of the database