""""
Description:
    Error handlers
    Some API errors are still handled globally and will return HTML unless json_response is specified
"""

from flask import render_template, request
from appPkg import db
from appPkg.errors import bp
from appPkg.api.errors import error_response


def wants_json_response():
    """
    Compares client preference for JSON or HTML for server response

    Returns
    -------
    boolean
        Preference between JSON (True) vs HTML (False)

    """
    #return request.accept_mimetypes['text/html'] # Force HTML for testing
    return request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']
        
@bp.app_errorhandler(404)
def not_found_error(error):
    """
    Handle 404 error

    Parameters
    ----------
    error : ?

    Returns
    -------
    HTML template or API error response
        
    """
   
    if wants_json_response():
        return error_response(404) # API error response
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    """
    Handle 500 error (eg database issues)

    Parameters
    ----------
    error : ?

    Returns
    -------
    HTML template or API error response
    
    """
    
    db.session.rollback()
    if wants_json_response():
        return error_response(500)  # API error response
    return render_template('errors/500.html'), 500
