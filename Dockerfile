FROM python:3.10-slim-buster
LABEL maintainer="FAroogh"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY ./requirements.txt /app/
COPY ./requirements.dev.txt /app/
COPY ./core /app

ARG DEV=false

RUN python -m venv /py &&\
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r requirements.dev.txt; \
    fi && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

ENV PATH="/py/bin:&PATH"

USER django-user