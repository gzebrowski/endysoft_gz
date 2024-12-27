FROM python:3.12-slim

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev curl gcc && \
    rm -rf /var/lib/apt/lists/*

COPY ["requirements.txt", "./"]
RUN pip install --no-cache --disable-pip-version-check -r requirements.txt

COPY ./src/ .
COPY .env /usr/src/app/

COPY ./docker/scripts/ /usr/src/scripts

RUN chmod +x /usr/src/scripts/init.sh
