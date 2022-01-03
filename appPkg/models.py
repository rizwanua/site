"""
Description:
    SQL database table setup 
"""

from flask import current_app, url_for
from flask_login import UserMixin

from datetime import datetime, timedelta
from time import time
from appPkg import db, login

from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
import jwt
import json

import base64
from datetime import datetime, timedelta
import os


class Stock(db.Model): 
    """
    Description:
        Stock table has all the stock symbols, prices, etc.
    """
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(300))
    active = db.Column(db.Boolean())
    lastPrice = db.Column(db.Float())
    lastUpdateTime = db.Column(db.DateTime())
    
    def __repr__(self):
        """
        Returns
        -------
        string
            Representation of Stock model.

        """
        return '<Stock {}>'.format(self.symbol)            
    
class User(UserMixin, db.Model): 
    """
    Description:
        User table contains user related information such as email, API tokens, etc
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    
    APItoken = db.Column(db.String(32), index=True, unique=True) 
    APItoken_expiration = db.Column(db.DateTime) 
    
    def __repr__(self):
        """
        Returns
        -------
        string
            Representation of User model.

        """
        return '<User {}>'.format(self.username)
    
    def set_password(self, password): 
        """
        Hash the user password.

        Parameters
        ----------
        password : string
            User password input (during registration).

        Returns
        -------
        None.

        """
        self.password_hash = generate_password_hash(password) 
 
    def check_password(self, password): 
        """
        Check if user input string password matches the hash.

        Parameters
        ----------
        password : string
            User password input (during login).

        Returns
        -------
        boolean
            Returns whether the input password matches the hash or not.

        """
        return check_password_hash(self.password_hash, password) 
    
    def get_reset_password_token(self, expires_in=1800): 
        """
        Returns a JWT token as a string. Example via Miguael Grinberg:
        
        >>> import jwt
        >>> token = jwt.encode({'a': 'b'}, 'my-secret', algorithm='HS256')
        >>> token
        'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhIjoiYiJ9.dvOo58OBDHiuSHD4uW88nfJik_sfUHq1mDi4G0'
        >>> jwt.decode(token, 'my-secret', algorithms=['HS256'])
        {'a': 'b'}

        Parameters
        ----------
        expires_in : integer, optional
            The default is 1800 seconds which is 30 minutes expiry.

        Returns
        -------
        JSON Web Token
            Encoded token to be sent via email to reset user password.

        """
           
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        """
        Verify the authentication token is valid and not expired.

        Parameters
        ----------
        token : JSON Web Token
            Encoded token sent via email to reset user password.

        Returns
        -------
        Dict
            Payload to verify correct user is resetting password.

        """
        
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
    
    def to_dict(self):
        """
        User model to JSON representation.
        Provide user information on API request.

        Returns
        -------
        data : dictionary
            Contains user information along with their alerts.

        """

        userData = self.getUserAlertData()
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'links': {
                'self': url_for('api.get_user', username=self.username)
            },
            'data': userData
        }
        return data
    
    def from_dict(self, data):
        """
        JSON representation to User model.
        Creates new user per API request.

        Parameters
        ----------
        data : dictionary
            Client entering data such as username and password to create new user.

        Returns
        -------
        None.

        """
        
        for field in ['username', 'email']:
            if field in data:
                setattr(self, field, data[field])
                
        # Set a password if registering a new user.
        if 'password' in data:
            self.set_password(data['password'])
    
    def get_APItoken(self, expires_in=3600):
        """
        Return API token to user. 
        Create a new one (with expire of 1 hour) if current token is expiring within a minute.

        Parameters
        ----------
        expires_in : seconds, optional
            The default is 3600 seconds (one hour)

        Returns
        -------
        string
            API token string.

        """

        now = datetime.utcnow()
        if self.APItoken and (self.APItoken_expiration > (now + timedelta(seconds=60))): 
            return self.APItoken # Return current token if it has atleast 1 minute left in expiry
        
        # Else, create a new token expiring 1 hour later
        self.APItoken = base64.b64encode(os.urandom(24)).decode('utf-8') # base64 - all characters in readable range
        self.APItoken_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.APItoken

    def revoke_APItoken(self):
        """
        Set API token expiry time.
        Allow user to revoke currently assigned API token by setting expiry to a second before current time

        Returns
        -------
        None.

        """

        self.APItoken_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_APItoken(APItoken):
        """
        Returns the user the token belongs to.

        Parameters
        ----------
        APItoken : string
            API token.

        Returns
        -------
        user : User object
            User object.

        """
        
        user = User.query.filter_by(APItoken=APItoken).first()
        if user is None or user.APItoken_expiration < datetime.utcnow():
            return None
        return user
    
    def getUserAlertData(self):
        """
        Aggregate all the alerts related data for the user

        Returns
        -------
        userAlerts : dictionary
            Data containing user alerts information.

        """
        
        alerts = alertTracker.query.filter_by(userID = self.id).all()
        
        alertID = []
        stockID = []
        symbol = []
        priceAtUserInput = []
        desiredPrice = []
        status = []
        
        for alert in alerts:
            # Get the stock data based off the Alert table.
            stock = Stock.query.filter_by(id=alert.stockID).first()
            
            # Add data to a list
            alertID.append('alertID:' + str(alert.id))
            stockID.append('stockID:' + str(stock.id))
            symbol.append('symbol:' + stock.symbol)
            priceAtUserInput.append('priceAtUserInput:' + str(alert.priceAtUserInput))
            desiredPrice.append('desiredPrice:' + str(alert.desiredPrice))
            status.append('status:' + alert.status)
        
        userAlerts = dict(zip(alertID, zip(*(map(str, lst) for lst in (stockID, symbol, priceAtUserInput, desiredPrice, status)))))
        
        return userAlerts
            
class alertTracker(db.Model): 
    """
    Description: 
        Tracks the alerts set by each user
    """
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'))
    stockID = db.Column(db.Integer, db.ForeignKey('stock.id'))
    
    priceAtUserInput = db.Column(db.Float()) 
    desiredPrice = db.Column(db.Float())
    status = db.Column(db.String(50)) # 'IN PROGRESS', 'ALERT TRIGGERED'
    
    
@login.user_loader 
def load_user(id):
    """
    Load user information based on ID. 

    Parameters
    ----------
    id : integer
        User object ID.

    Returns
    -------
    User instance
        User object instance in the DB.

    """
    
    return User.query.get(int(id)) 
