# Stock Price Alert
Stock Price Alert allows a user to create price alerts for stock tickers listed on the NASDAQ Global MarketSM exchange. The user will receive an email notification once their alert has been triggered.

The app has been created to demonstrate understanding of back-end web development, HTTP requests and responses, RESTful API, SQL databases, and more.

## Tools and tech stack used include:
- Flask framework in Python 3.8
- Docker containers
- Amazon AWS services (EC2/ECR/ECS/RDS-PostgreSQL)
- GitHub CI/CD deployment actions

Credits to the [Flask Mega-Tutorial by Miguel Grinberg][tutorial]. Some modules of this app (such as login authentication and structuring the API framework) have been re-used from the tutorial with modifications as appropriate.

## Features
- API Access - API access is available to interact with the app without a web browser.
- Manage Stock Alerts - Allows the user to create a stock price alert. The user will receive an email notification when the stock moves to the desired price.

## Project Status
While a working prototype has been deployed, the project continues to remain under development with additional features, error handling, and updates.

## Installation
**Local Server**
- Create a virtual Python environment in a local directory ("python -m venv venv" for Windows).
- Download the GitHub repo. 
- Install the library dependencies per the requirements.txt file
- Create a '.env' file with environment variables (See "docker build --build-arg" within "site/.github/workflows/aws.yml" for all the required variables.)
- Execute 'flask run' and access the app via "http://localhost:5000/"

**Production Environment**
- Go through the [Flask to ECS][FlaskToECS] tutorial to setup a domain name, AWS EC2 server, AWS ECR repository for Docker images, AWS ECS container service, PostgreSQL database using AWS RDS, and GitHub Secrets to load the environment variables.
- Deploy the app via Docker using GitHub CI/CD actions pipeline to AWS.


## Files Walkthrough

| File|About            |
|----------------|-------------------------------|
|/.github/workflows/aws.yml|GitHub Workflow to create and deploy Docker image to AWS|
|appPkg          |Flask files. More details below            |
|migrations          |Data containing SQLAlchemy database migrations|
| .gitignore|Local files to be ignored when commiting to GitHub|
|Dockerfile|Commands to build a Docker image.|
|aws-task-definition.json|Instructions required to run Docker containers in AWS ECS. Copy/paste from AWS directly|
|boot.sh|Start up script for Docker|
|config.py|Contains all data configurations to import environment variables, and "magic numbers" used by the app|
|requirements.txt|Contains all Python library dependencies for this app|
|stockpricealert.py|Entry point to the app|

| appPkg Files         |About            |
|-----------------------|-------------------------------|
|/api|Contains files related to the API interaction between client and server|
|/auth|Contains files related to website registration, login, and user authentication|
|/errors|Error handling for the app|
|/main|Contains files related to the main functionality of the app to create and delete Stock Alerts, and email alert notifications to the user.|
|/templates|Contains HTML files for the website front-end.|
|__init__.py|Initializes the Flask app, invokes Flask extension instances, registers blueprints, and initializes SMTP handling to email log errors.|
|email.py|Handles sending of emails to website admin and users.|
|models.py|Classes containing SQL database structure and associated functions.|


   
   [tutorial]: <https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world>
   [FlaskToECS]: <https://www.youtube.com/watch?v=kqa_cchAMLY&list=PL0dOL8Z7pG3IWsvseNd-JoFTHL16P_iTC>
