FROM python:3.8-slim
# python 3.9 does not support backports.zoneinfo==0.2.1 (https://github.com/pganssle/zoneinfo/issues/105)

# to install python package psycopg2 (for postgres)
RUN apt-get update
RUN apt-get install -y postgresql libpq-dev postgresql-client postgresql-client-common gcc

# add user - prevents sudo commands
RUN useradd stockpricealert

# set current env
ENV HOME /app
WORKDIR /app
ENV PATH="/app/.local/bin:${PATH}"

RUN chown -R stockpricealert:stockpricealert ./


# set argument vars in docker-run command
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION
ARG AWS_S3_BUCKET
# flask form key
ARG SECRET_KEY
# AWS RDS vars
ARG POSTGRES_USER
ARG POSTGRES_PW
ARG POSTGRES_URL
ARG POSTGRES_DB
# Email support
ARG MAIL_PORT
ARG MAIL_SERVER
ARG MAIL_USE_TLS
ARG MAIL_USERNAME
ARG MAIL_PASSWORD
ARG ADMINS

ENV AWS_ACCESS_KEY_ID $AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY $AWS_SECRET_ACCESS_KEY
ENV AWS_DEFAULT_REGION $AWS_DEFAULT_REGION
ENV AWS_S3_BUCKET $AWS_S3_BUCKET
ENV SECRET_KEY $SECRET_KEY
ENV POSTGRES_USER $POSTGRES_USER
ENV POSTGRES_PW $POSTGRES_PW
ENV POSTGRES_URL $POSTGRES_URL
ENV POSTGRES_DB $POSTGRES_DB
ENV MAIL_PORT $MAIL_PORT
ENV MAIL_SERVER $MAIL_SERVER
ENV MAIL_USE_TLS $MAIL_USE_TLS
ENV MAIL_USERNAME $MAIL_USERNAME
ENV MAIL_PASSWORD $MAIL_PASSWORD
ENV ADMINS $ADMINS

# Add files
COPY appPkg /app/appPkg
COPY migrations /app/migrations
COPY stockpricealert.py config.py boot.sh /app/
RUN chmod +x /app/boot.sh

# Requirements
COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install --no-cache-dir -r requirements.txt
RUN venv/bin/pip install gunicorn

ENV FLASK_APP stockpricealert.py

USER stockpricealert

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]