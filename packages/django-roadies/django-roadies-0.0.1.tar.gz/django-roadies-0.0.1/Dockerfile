FROM anthonyalmarza/alpine-pyenv:cable

MAINTAINER Anthony Almarza <anthony.almarza@gmail.com>

WORKDIR /var/django-roadies

COPY requirements-dev.txt requirements-dev.txt

VOLUME ['/var/django-roadies']

RUN pip install -r requirements-dev.txt
