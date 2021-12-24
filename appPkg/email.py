from flask_mail import Message
from appPkg import mail
from threading import Thread
from flask import current_app

'''
Sending an email slows the application down considerably

What I really want is for the send_email() function to be asynchronous. 
What does that mean? It means that when this function is called, the task of sending the email is scheduled to happen in the background, freeing the send_email() to return immediately so that the application can continue running concurrently with the email being sent.

Python has support for running asynchronous tasks, actually in more than one way. 
The threading and multiprocessing modules can both do this. Starting a background thread for email being sent is much less resource intensive than starting a brand new process, so I'm going to go with that approach:
'''

def send_async_email(app, msg):
    '''
    The send_async_email function now runs in a background thread, invoked via the Thread class in the last line of send_email().
    With this change, the sending of the email will run in the thread, and when the process completes the thread will end and clean itself up
        
    You probably expected that only the msg argument would be sent to the thread, but as you can see in the code, I'm also sending the application instance. 
    When working with threads there is an important design aspect of Flask that needs to be kept in mind
    Flask uses contexts to avoid having to pass arguments across functions. I'm not going to go into a lot of detail on this, but know that there are two types of contexts, the application context and the request context
    In most cases, these contexts are automatically managed by the framework, but when the application starts custom threads, contexts for those threads may need to be manually created.
    
    There are many extensions that require an application context to be in place to work, because that allows them to find the Flask application instance without it being passed as an argument
    The reason many extensions need to know the application instance is because they have their configuration stored in the app.config object
    This is exactly the situation with Flask-Mail. The mail.send() method needs to access the configuration values for the email server, and that can only be done by knowing what the application is
    The application context that is created with the with app.app_context() call makes the application instance accessible via the current_app variable from Flask
    '''
    with app.app_context():
        mail.send(msg)

'''
Using current_app directly in the send_async_email() function that runs as a background thread would not have worked, because current_app is a context-aware variable that is tied to the thread that is handling the client request
In a different thread, current_app would not have a value assigned
Passing current_app directly as an argument to the thread object would not have worked either, because current_app is really a proxy object that is dynamically mapped to the application instance
So passing the proxy object would be the same as using current_app directly in the thread

What I needed to do is access the real application instance that is stored inside the proxy object, and pass that as the app argument
The current_app._get_current_object() expression extracts the actual application instance from inside the proxy object, so that is what I passed to the thread as an argument
'''
def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
    
