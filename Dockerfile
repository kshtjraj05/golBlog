FROM python:3.8.2-alpine3.11

RUN adduser -D golblog

WORKDIR /home/golblog

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN python -m pip install --upgrade setuptools pip wheel
RUN apk add --no-cache python3-dev openssl-dev libffi-dev gcc
RUN apk add --no-cache make gcc musl-dev
RUN apk add --no-cache g++
RUN apk add build-base python-dev py-pip jpeg-dev zlib-dev
ENV LIBRARY_PATH=/lib:/usr/lib
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn       

COPY flaskblog flaskblog
COPY migrations migrations
COPY run.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP run.py

RUN chown -R golblog:golblog ./
USER golblog

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]

