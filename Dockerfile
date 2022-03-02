FROM python:3.10.2-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION 1.1.13

ARG UNAME=testuser
ARG UID=5000
ARG GID=5000

# Create custom user (the same that runs docker-compose)
RUN groupadd -g $GID $UNAME
RUN useradd -m -u $UID -g $GID -os /bin/bash $UNAME

# Run poetry installation
RUN python -m pip install --upgrade pip
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /code
RUN chown $USER_ID:$GROUP_ID .
USER $UNAME
COPY poetry.lock pyproject.toml /code/

# Project initialization:
RUN poetry config virtualenvs.create false && poetry install

# Creating folders, and files for a project:
ADD . /code/

WORKDIR /code/config
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "config.wsgi:application"]