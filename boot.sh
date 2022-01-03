#!/bin/bash
# Docker container start-up script
# activate the virtual environment, upgrade the database though the migration framework, and run the server with gunicorn

source venv/bin/activate

exec gunicorn -b :5000 --access-logfile - --error-logfile - stockpricealert:app