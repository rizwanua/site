"""
Description:
    Create and retrieve user information via the API
"""
from flask import jsonify, url_for, request
from appPkg import db
from appPkg.models import User
from appPkg.api import bp
from appPkg.api.errors import bad_request
from appPkg.api.auth import APItoken_auth


@bp.route('/users/<username>', methods=['GET'])
@APItoken_auth.login_required
def get_user(username):
    """
    Get user information via API

    Parameters
    ----------
    username : string
        Username of user.

    Returns
    -------
    JSON
        JSON dictionary of user instance.

    """

    # Generate dict with resource rep defined in User model, jsonify converts dict to JSON to return to client
    return jsonify(User.query.filter_by(username=username).first_or_404().to_dict()) # Returns 404 instead of None if there is no object.

@bp.route('/users', methods=['POST'])
def create_user():
    """
    Create new user via API.
    No @APItoken_auth.login_required decorator since there is no authentication available for new user.

    Returns
    -------
    JSON
        JSON containing user data plus HTTP status codes and headers.
    """

    data = request.get_json() or {} # Extract JSON from the request and return it as a Python structure
    
    # Check mandatory fields as well as duplicate information.
    if ('username' or 'email' or 'password') not in data:
        return bad_request('Please include username, email and password fields')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('Username already exists. Please use a different username.')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('Email already exists. Please use a different email address.')
    
    # Create user object and add to DB
    user = User()
    user.from_dict(data)
    db.session.add(user)
    db.session.commit()
    
    # Reply back with user information
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', username=user.username) # HTTP protocol requires that a 201 response includes a Location header that is set to the URL of the new resource
    return response

'''
Future Improvement - Allow user to change own email address

@bp.route('/users/<username>', methods=['PUT'])
@APItoken_auth.login_required
def update_user(id):
    pass
'''