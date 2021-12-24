### 
### Authentication - Blueprint creation
### 

from flask import Blueprint

bp = Blueprint('auth', __name__)

from appPkg.auth import routes
