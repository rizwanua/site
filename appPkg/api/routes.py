"""
Description:
    Routes for API related tasks
"""

from appPkg.main import bp
from flask import render_template, flash, redirect, url_for, current_app, request, session
from flask_login import current_user, login_required
from appPkg.api import bp
from appPkg.main.syslog import logInfo

@bp.route('/apidoc', methods=['GET'])
def apidocs():
    """
    Flask route for API document

    Returns
    -------
    HTML
        API document HTML.

    """
    if current_user.is_authenticated:
        logInfo(f'APIdoc as user {current_user.id}') # Log client information
    else:
        logInfo(f'APIdoc as anonymous') # Log client information
       
    return render_template('api/apidoc.html', title='API Documentation')

