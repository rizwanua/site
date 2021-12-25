#!/bin/bash
# Docker container start-up script
# activate the virtual environment, upgrade the database though the migration framework, and run the server with gunicorn

# it takes a few seconds for this container to be fully running and ready to accept database connections
# you start the MySQL container and then start the application container immediately after, when the boot.sh script tries to run flask db upgrade it may fail due to the database not being ready to accept connections
# This loop checks the exit code of the flask db upgrade command, and if it is non-zero it assumes that something went wrong, so it waits five seconds and then retries

source venv/bin/activate

exec gunicorn -b :5000 --access-logfile - --error-logfile - stockpricealert:app