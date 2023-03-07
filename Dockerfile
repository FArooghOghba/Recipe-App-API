FROM python:3.10-slim-buster
LABEL maintainer="FAroogh"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY ./requirements.txt /app/
COPY ./requirements.dev.txt /app/
COPY ./core /app

ARG DEV=false

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    if [$DEV = "true"]; \
        then pip install -r requirements.dev.txt; \
    fi && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

USER django-user