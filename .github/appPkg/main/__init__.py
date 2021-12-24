from flask import Blueprint

bp = Blueprint('main', __name__)

from appPkg.main import routes
