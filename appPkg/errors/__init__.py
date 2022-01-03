"""
Description:
    Errors blueprint
"""

from flask import Blueprint

bp = Blueprint('errors', __name__)

from appPkg.errors import handlers