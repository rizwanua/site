"""
Description:
    Log client info 
"""

from flask import request
import logging

def logInfo(page = None, module = None, current_user=None):
    """
    Write client information into logs

    Parameters
    ----------
    page : string, optional
        The default is None. Normally contains a string of the page client is trying to access and user info

    current_user : user, optional
        The default is None. Normally contains a user data if authenticated on website.
        
    Returns
    -------
    None.

    """
    
    # Get user ID if the user is accessing after authentication
    userId = '?'
    if current_user and current_user.is_authenticated:
        userId = current_user.id 
        
    # Get user client IP address. 
    # This may be spoofed by client - https://stackoverflow.com/questions/12770950/flask-request-remote-addr-is-wrong-on-webfaction-and-not-showing-real-user-ip
    if request.headers.getlist("X-Forwarded-For"):
       ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
       ip = request.remote_addr
      
    # Log data
    log = logging.getLogger(__name__)
    log.info(f'IP: {ip} - User: {userId} - Accessing: {page} in {module}. ') # Log client information