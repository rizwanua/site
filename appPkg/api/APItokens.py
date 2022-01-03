"""
Description:
    API authentication via tokens
"""

from flask import jsonify
from appPkg import db
from appPkg.api import bp
from appPkg.api.auth import basic_auth, APItoken_auth

@bp.route('/APItokens', methods=['POST'])
@basic_auth.login_required
def get_APItoken():
    """
    Get API token for user

    Returns
    -------
    JSON
        API token

    """

    APItoken = basic_auth.current_user().get_APItoken()
    db.session.commit()
    return jsonify({'APItoken': APItoken})

@bp.route('/APItokens', methods=['DELETE'])
@APItoken_auth.login_required
def revoke_APItoken():
    """
    Delete users API token

    Returns
    -------
    <args>
        Empty string for message, HTTP status code 204

    """

    APItoken_auth.current_user().revoke_APItoken()
    db.session.commit()
    return '', 204 # Return empty string with 204 (successful request with no response)