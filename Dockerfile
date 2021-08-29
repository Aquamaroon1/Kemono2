FROM ubuntu:18.04

RUN apt-get update \
    && apt-get install -y \
        python3 \
        python3-dev \
        python3-pip \
        libpq-dev \
        curl \
    && pip3 install uwsgi

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . /app

ENV LANG=C.UTF-8

CMD uwsgi --ini ./uwsgi.ini
