FROM python:3.7-alpine

RUN useradd stockpricealert

WORKDIR /home/stockpricealert

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install --no-cache-dir -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY appPkg appPkg
COPY migrations migrations
COPY stockpricealert.py config.py 

ENV FLASK_APP stockpricealert.py

RUN chown -R stockpricealert:stockpricealert ./
USER stockpricealert

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
