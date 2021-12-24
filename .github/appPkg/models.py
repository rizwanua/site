from datetime import datetime, timedelta
from appPkg import db, login
from flask import current_app, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
import json

import base64
from datetime import datetime, timedelta
import os


class Stock(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(300))
    active = db.Column(db.Boolean())
    lastPrice = db.Column(db.Float())
    lastUpdateTime = db.Column(db.DateTime())
    
    def __repr__(self):
        return '<Stock {}>'.format(self.symbol)
  
            
    
class User(UserMixin, db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password): 
        self.password_hash = generate_password_hash(password) 
 
    def check_password(self, password): 
        return check_password_hash(self.password_hash, password) 
    
    def get_reset_password_token(self, expires_in=1800): #30 min expiry
        '''
        returns a JWT token as a string
        '''
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod # invoked directly from the class. A static method is similar to a class method, with the only difference that static methods do not receive the class as a first argument
    def verify_reset_password_token(token):
        '''
        - If the token cannot be validated or is expired, an exception will be raised, and in that case I catch it to prevent the error, and then return None to the caller.
        - If the token is valid, then the value of the reset_password key from the token's payload is the ID of the user, so I can load the user and return it.
        '''
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
    
class alertTracker(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'))
    stockID = db.Column(db.Integer, db.ForeignKey('stock.id'))
    
    priceAtUserInput = db.Column(db.Float()) 
    desiredPrice = db.Column(db.Float())
    status = db.Column(db.String(50)) # 'IN PROGRESS', 'USER ALERTED'
    lastCheckTime = db.Column(db.DateTime())
    
    #currentPrice - priceAtUserInput >= priceDiff # for True UP
    #currentPrice - priceAtUserInput <= priceDiff # for False DOWN
    


@login.user_loader # user loader is registered with Flask-Login with the @login.user_loader decorator
def load_user(id):
    return User.query.get(int(id)) # id that Flask-Login passes to the function as an argument is going to be a string, so databases that use numeric IDs need to convert the string to integer
