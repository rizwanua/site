"""
Description:
    Routes for API related tasks
"""

from appPkg.main import bp
from flask import render_template, flash, redirect, url_for, current_app, request, session
from flask_login import current_user, login_required
from appPkg.api import bp
from appPkg.main.syslog import logInfo
import inspect

@bp.route('/apidoc', methods=['GET'])
def apidocs():
    """
    Flask route for API document

    Returns
    -------
    HTML
        API document HTML.

    """
    
    logInfo(inspect.stack()[0].function, __name__, current_user) # Log page access information
    
       
    return render_template('api/apidoc.html', title='API Documentation')

