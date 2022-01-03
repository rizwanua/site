"""
Description:
    - Email handling for registration, app errors, etc
    - Run asynchronously via threading to allow main app thread to continue processing
"""

from flask_mail import Message
from appPkg import mail
from threading import Thread
from flask import current_app

def send_async_email(app, msg):
    """
    Calls the Flask-Mail instance to email email via a separate thread

    Parameters
    ----------
    app : Flask instance
        New thread needs access to Flask configuration
        
    msg : String
        Email message containing subject, sender, recipient, and body data.

    Returns
    -------
    None.

    """
        
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    """
    Sets up the msg parameter and initiates new thread

    Parameters
    ----------
    subject : string
        Email subject.
    sender : string
        Admin email address.
    recipients : string
        Recipient email address.
    text_body : text
        Email text in text form.
    html_body : HTML
        Email text in HTML form.

    Returns
    -------
    None.

    """

    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
    
