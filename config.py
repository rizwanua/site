import os
from dotenv import load_dotenv

'''
Alternative approach: app.config['SECRET_KEY'] = 'you-will-never-guess' within \appPkg\__init__.py
Configuration settings are defined as class variables inside the Config class

'''

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env')) # Non-flask specific environment variables

class Config(object):
    
    # Secret key config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'something-secret-3%1~'
    
    # Database config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Disable a signal sent to the application every time a change is about to be made in the database.
    
    # NUMBER OF ALERTS AVAILABLE PER USER
    ALERTS_PER_USER = 5
    
    # Email configuration to send errors
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = [os.environ.get('ADMINS')]