'''
Error handlers
'''

from flask import render_template, request
from appPkg import db
from appPkg.errors import bp
#from appPkg.api.errors import error_response as api_error_response

'''
Note that both functions return a second value after the template, which is the error code number. 
For all the view functions that I created so far, I did not need to add a second return value because the default of 200 (the status code for a successful response) is what I wanted. 
In this case these are error pages, so I want the status code of the response to reflect that.

The error handler for the 500 errors could be invoked after a database error, which was actually the case with the username duplicate above. 
To make sure any failed database sessions do not interfere with any database accesses triggered by the template, I issue a session rollback.
This resets the session to a clean state.


API Friendly Error Messages
If server returns a 404, error is normally formatted as the standard 404 HTML error page
Many of the errors the API might need to return can be overriden with JSON versions in the API blueprint, 
but there are some errors handled by Flask that still go through the error handlers that are globally registered for the application, and these continue to return HTML

The HTTP protocol supports a mechanism by which the client and the server can agree on the best format for a response, called content negotiation
The client needs to send an Accept header with the request, indicating the format preferences
The server then looks at the list and responds using the best format it supports from the list offered by the client.

modify the global application error handlers so that they use content negotiation to reply in HTML or JSON according to the client preferences
This can be done using the request.accept_mimetypes object from Flask:

'''
def wants_json_response():
    '''
    The wants_json_response() helper function compares the preference for JSON or HTML selected by the client in their list of preferred formats
    If JSON rates higher than HTML, then I return a JSON response
    Otherwise I'll return the original HTML responses based on templates
    '''
    return request.accept_mimetypes['text/html']
   #return request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']
        
@bp.app_errorhandler(404)
def not_found_error(error):
    '''
    For the JSON responses I'm going to import the error_response helper function from the API blueprint, 
    but here I'm going to rename it to api_error_response() so that it is clear what it does and where it comes from
    '''
    #if wants_json_response():
    #    return api_error_response(404)
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    #if wants_json_response():
    #    return api_error_response(500)
    return render_template('errors/500.html'), 500
