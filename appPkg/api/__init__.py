"""
Description:
    API blueprint
"""

from flask import Blueprint

bp = Blueprint('api', __name__)

from appPkg.api import users, errors, routes, APItokens
