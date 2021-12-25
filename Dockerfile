FROM python:slim

RUN useradd stockpricealert

WORKDIR /home/stockpricealert

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install --no-cache-dir -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY appPkg appPkg
COPY migrations migrations
COPY stockpricealert.py app.db config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP stockpricealert.py

RUN chown -R stockpricealert:stockpricealert ./
USER stockpricealert

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]