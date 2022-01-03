"""
Description:
    API errors
"""

from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES


def error_response(status_code, message=None):
    """
    Create an error response with the HTTP status code and message if applicable

    Parameters
    ----------
    status_code : integer
        HTTP status code.
    message : String, optional
        The default is None. 

    Returns
    -------
    response : JSON
        Return error with status codes and message if appliable.

    """

    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload) # jsonify() function returns a Flask Response object with a default status code of 200
    response.status_code = status_code # After response created above, set status code to the appropriate error
    return response


def bad_request(message):
    """
    Return 400 when client requests invalid data

    Parameters
    ----------
    message : string
        Message to add to the error response.

    Returns
    -------
    HTTP type response
        Error response to user.

    """

    return error_response(400, message)
