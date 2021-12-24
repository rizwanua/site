### 
### Errors - Blueprint creation
### 

from flask import Blueprint

'''
The Blueprint class takes the name of the blueprint, the name of the base module (typically set to __name__ like in the Flask application instance
After the blueprint object is created, I import the handlers.py module, so that the error handlers in it are registered with the blueprint
This import is at the bottom to avoid circular dependencies
'''

bp = Blueprint('errors', __name__)

from appPkg.errors import handlers