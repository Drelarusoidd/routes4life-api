FROM python:3.10.2-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION 1.1.13
ENV DEBUG 1

ARG UNAME=testuser
ARG UID=5000
ARG GID=5000

# Create custom user (the same that runs docker-compose)
RUN groupadd -g $GID $UNAME
RUN useradd -m -u $UID -g $GID -os /bin/bash $UNAME

# Run poetry installation
RUN python -m pip install --upgrade pip
RUN pip install "poetry==$POETRY_VERSION"

# Conncetion to Debian repo for PostgreSQL
RUN apt update -y && apt upgrade -y
RUN apt -y install gnupg2 wget vim
RUN apt-cache search postgresql | grep postgresql
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt buster-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN apt -y update

# PostgreSQL-14 client, server, contrib, etc.
RUN apt -y install postgresql-14

# Necessary libs for GDAL, GEOS and PROJ
RUN apt-get update \
    && apt-get -y install netcat gcc \
    && apt-get clean
RUN apt-get update \
    && apt-get install -y binutils libproj-dev gdal-bin python-gdal python3-gdal

# Copy only requirements to cache them in docker layer
WORKDIR /code
RUN chown $USER_ID:$GROUP_ID .
USER $UNAME
COPY poetry.lock pyproject.toml /code/

# Project initialization:
RUN poetry config virtualenvs.create false && poetry install
RUN poetry show --tree

# Creating folders, and files for a project:
COPY . /code/
WORKDIR /code/config

# Run server in production mode
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "config.wsgi:application"]
