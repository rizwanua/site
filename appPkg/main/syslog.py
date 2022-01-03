"""
Description:
    Log client info 
"""

from flask import request
import logging

def logInfo(page=None):
    """
    Write client information into logs

    Parameters
    ----------
    page : string, optional
        The default is None. Normally contains a string of the page client is trying to access and user info

    Returns
    -------
    None.

    """
    
    # Get user client IP address. 
    # This may be spoofed by client - https://stackoverflow.com/questions/12770950/flask-request-remote-addr-is-wrong-on-webfaction-and-not-showing-real-user-ip
    if request.headers.getlist("X-Forwarded-For"):
       ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
       ip = request.remote_addr
       
    log = logging.getLogger(__name__)
    log.info(f'IP: {ip} - Access: {page}') # Log client IP address