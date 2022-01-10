"""
Description:
    - Log client info in logger
    - Backup log files to AWS S3
"""

import logging
import boto3
import os

from datetime import datetime
from botocore.exceptions import ClientError
from flask import request, current_app
from threading import Thread

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
    
    
    
def upload_file_to_s3(app, file_name, bucket, folder_name=None):
    """
    Modified as needed from https://medium.com/@pushp1997/use-python-boto3-to-backup-files-logs-to-aws-s3-df34cf93d214
    Upload a file to an AWS S3 bucket.
    
    Parameters
    ----------
    app : Flask instance
    file_name : str
        File to upload.
    bucket : str
        Bucket to upload to.
    folder_name : str, optional
        Folder name in which file is to be uploaded. The default is None.

    Returns
    -------
    None.

    """
    
    with app.app_context():
        # S3 object_name is file_name
        object_name = file_name.split('/')[-1]
        
        # If folder_name was specified, upload in the folder
        if folder_name is not None:
            object_name = f'{folder_name}/{object_name}'
        
        print('file :', file_name, 'bucket :', bucket, 'object:', object_name)
        
        # Upload the file
        try:
            s3_client = boto3.client(
                service_name='s3',
                region_name=current_app.config['AWS_DEFAULT_REGION'],
                aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY']
            )
            s3_client.upload_file(file_name, bucket, object_name)
            
        except ClientError as e:
            log = logging.getLogger(__name__)
            log.info(e)
            print('ERROR:::: \n', e)
 
        
def backup_logs(app, directory):
    """
    Determine if any log files need to be uploaded to the S3 bucket.

    Parameters
    ----------
    app : Flask instance
    directory : str
        Current working directory.

    Returns
    -------
    None.

    """
    
    with app.app_context():
        
        log_files = [] # Initialize log files to upload         
        directory  = directory + '/logs' # Set to logs directory

        # Loop through logs directory, get file modified time, compare to last logTimeCheck
        for file in os.listdir(os.fsencode(directory)):
            filename = os.fsdecode(file)
            filepath = os.path.join(directory, filename)
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            # Check if file as modified since last check
            if mtime >= current_app.logTimeCheck:
                log_files.append(filepath)
        
        # Update the logTimeCheck to the current time to prevent unnecessary uploads to S3.                
        current_app.logTimeCheck = datetime.now()
        
        # Call upload_file_to_s3 in new thread for any log files needing to be uploaded
        if log_files:
            for log_file in log_files:
                Thread(target=upload_file_to_s3, args=[current_app._get_current_object(), log_file, current_app.config['AWS_S3_BUCKET'], 'logs']).start()
    