"""
Description:
    Verification of user password and API tokens
"""

from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from appPkg.models import User
from appPkg.api.errors import error_response

basic_auth = HTTPBasicAuth() # Username/password authentication
APItoken_auth = HTTPTokenAuth() # API token authentication

@basic_auth.verify_password
def verify_password(username, password):
    """
    Before API access can be granted, verify username and password.

    Parameters
    ----------
    username : string
        Username string input by user
    password : string
        Password string input by user

    Returns
    -------
    User instance
        
    """

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user # Available as basic_auth.current_user()

@basic_auth.error_handler
def basic_auth_error(status_code):
    """
    Return error if incorrect username/password passed in via API

    Parameters
    ----------
    status_code : integer
        HTTP status code.

    Returns
    -------
    JSON
        HTTP error response.

    """

    return error_response(status_code)


@APItoken_auth.verify_token
def verify_APItoken(APItoken):
    """
    Returns user that owns the provided token.
    Return of None will cause rejection to client

    Parameters
    ----------
    APItoken : string
        API token.

    Returns
    -------
    User instance
        Returns the user the token belongs to.

    """

    return User.check_APItoken(APItoken) if APItoken else None

@APItoken_auth.error_handler
def APItoken_auth_error(status_code):
    """
    Return error if incorrect token passed in via API

    Parameters
    ----------
    status_code : integer
        HTTP status code.

    Returns
    -------
    Error response with HTTP status code and message if applicable
    """

    return error_response(status_code)
