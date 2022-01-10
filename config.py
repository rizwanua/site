import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env')) # Local - Non-flask specific environment variables

class Config(object):
    
    # Secret key config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'something-secret-3%1~'
    
    # Database config - For local app.db testing
    '''
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    '''
    
    # AWS access (ie to S3)
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET')
    AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION')
    
    # Database config - For AWS RDS PostgreSQL
    SQLALCHEMY_DATABASE_URI = (
        f'postgresql+psycopg2://{os.environ.get("POSTGRES_USER")}:' +
        f'{os.environ.get("POSTGRES_PW")}@{os.environ.get("POSTGRES_URL")}/{os.environ.get("POSTGRES_DB")}'
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Disable a signal sent to the application every time a change is about to be made in the database.
    
    # NUMBER OF ALERTS ALLOWED PER USER
    ALERTS_PER_USER = 5
    
    # ALERT NOTIFICATION CHECKING FREQUENCY (in seconds)
    ALERT_CHECK_FREQUENCY = 600 # 10 minutes * 60 seconds/min
    
    # CURRENT PRICE CHECK FREQUENCY (in minutes)
    PRICE_CHECK_FREQUENCY = 9
    
    # AWS S3 BACKUP FREQUENCY (in seconds)
    LOG_BACKUP_FREQUENCY = 10 # 1 minute * 60 seconds/min
    
    # Email configuration to send errors
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = [os.environ.get('ADMINS')]
    