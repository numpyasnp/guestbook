FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONPATH=/app/guest_book

WORKDIR /app

# System deps
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy project
COPY . /app

# Env
ENV DJANGO_SETTINGS_MODULE=guest_book.settings \
    PORT=8000 \
    GUNICORN_WORKERS=3 \
    GUNICORN_BIND=0.0.0.0:8000

EXPOSE 8000

# Run migrations and start server
CMD python guest_book/manage.py migrate --noinput && \
    gunicorn guest_book.wsgi:application \
    --workers ${GUNICORN_WORKERS} \
    --bind ${GUNICORN_BIND} \
    --timeout 60
