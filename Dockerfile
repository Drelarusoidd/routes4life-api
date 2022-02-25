FROM python:3.10.2-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION 1.1.13

RUN python -m pip install --upgrade pip
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Project initialization:
RUN poetry config virtualenvs.create false && poetry install

# Creating folders, and files for a project:
COPY . /code/

WORKDIR /code/config
RUN python manage.py collectstatic --no-input
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "config.wsgi:application"]