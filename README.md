## Guestbook API

[![Build](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/USER/guestbook/actions)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x-092E20)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED)](https://www.docker.com/)

A modern Guestbook REST API. Users can submit messages (entries), list them with pagination, and benefit from performance optimizations powered by Django, PostgreSQL, and Redis.

### Summary
- RESTful API for managing users and entries (CRUD endpoints for core flows).
- PostgreSQL database and Redis caching for performance and scalability.
- Ready for local development and deployment via Docker.

## Features
- **RESTful API** for `User` and `Entry` models
  - `POST /api/v1/entries` to create a new entry (automatically creates the user if not exists)
  - `GET /api/v1/entries` to list entries with pagination (newest first)
  - `GET /api/v1/users` to get users with total entry count and last entry summary
- **Fake data generation**: High‑volume test data via `manage.py generate_fake_data`
- **Unit tests**: Comprehensive tests for core functionality
- **Performance**:
  - `select_related`, `bulk_create`, and proper indexes in queries
  - Redis-backed pagination and response caching
- **Turkish text utilities**: `turkish_str` helpers for Turkish characters and case sensitivity handling

## Architecture & Stack
- **Runtime**: Python 3.10+, Django 5.x, Django REST Framework
- **Database**: PostgreSQL 16 (default database `guestbook`)
- **Cache**: Redis (default `redis://127.0.0.1:6379/1`)
- **Others**: drf-spectacular, django-extensions, Faker, Gunicorn, Nginx (via Docker)

## Project Layout (abridged)
```text
guest_book/
  api/            # REST API: urls/serializers/views
  entry/          # Entry app (model, admin, tests, fake data command)
  user/           # User app (model, admin, tests)
  libs/           # Shared utilities (e.g., normalize/turkish_str)
```

## Setup
### 1) Quickstart with Docker
```bash
# Clone the repo
git clone https://github.com/numpyasnp/guestbook.git
cd guestbook

# Create environment file
cp env.example .env

# Start services
docker compose up -d --build
```

### 2) Local Python Environment
```bash
# Python 3.10+ required
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp env.example .env

# Ensure PostgreSQL is running and the .env values are correct
# Defaults: DB_NAME=guestbook, DB_USER=guest, DB_PASSWORD=guest, DB_HOST=localhost, DB_PORT=5432

python guest_book/manage.py migrate
python guest_book/manage.py runserver 0.0.0.0:8000
```

### Environment Variables
Configured via `.env`:
- `DEBUG` (default: `1`)
- `SECRET_KEY`
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `CACHE_URL` (e.g., `redis://127.0.0.1:6379/1`)

## Usage
### API Endpoints
- **Entry**
  - `POST /api/v1/entries`
  - `GET /api/v1/entries`
- **User**
  - `GET /api/v1/users`

### Examples
Create an entry:
```bash
curl -X POST http://localhost:8000/api/v1/entries \
  -H 'Content-Type: application/json' \
  -d '{
        "name": "John Doe",
        "subject": "Great experience",
        "message": "This site is very helpful, thanks!"
      }'
```

List entries (paginated):
```bash
curl 'http://localhost:8000/api/v1/entries?page=1'
```

User summary:
```bash
curl 'http://localhost:8000/api/v1/users'
```

### Generate Fake Data (inside Docker container)
Run the management command inside the `web` service container:
```bash
docker compose exec web python guest_book/manage.py generate_fake_data --users 1000 --entries 10000 --batch 1000
```
Parameters:
- `--users`: Number of users to create (default 1000)
- `--entries`: Number of entries to create (default 10000)
- `--batch`: `bulk_create` batch size (default 1000)

## Tests (inside Docker container)
```bash
docker compose exec web python guest_book/manage.py test entry user
```

## Performance Notes
- **Query optimization**: `select_related("user")`, proper ordering, and `bulk_create` for data generation.
- **Caching**: Redis-based caching for pagination and user listing (configured via `CACHE_URL`).
- **Indexes**: Migrations define helpful indexes (e.g., for date/order).
- **DB-level computations (annotations)**: Use QuerySet annotations (Count, Subquery, Concat, etc.) to compute per-user totals and latest entry summaries directly in the database, reducing round-trips and N+1 queries.

## Turkish Text Handling
- `libs/normalize.py` provides `turkish_str` helper and `TurkishStr` class for Turkish-aware casing and character handling.
- Example in practice: fake data generation normalizes names with `title()` using Turkish rules.

Recommended commands:
```bash
# Pre-commit
pre-commit install
pre-commit run --all-files
```

## Deployment
- Served with Gunicorn; static files via Nginx (Docker setup included).
- Configure `ALLOWED_HOSTS`, `SECRET_KEY`, set `DEBUG=0`, and review DB/cache configuration for production.

## Troubleshooting
- Database: If `psycopg2` errors occur, verify PostgreSQL service and `DB_*` values.
- Cache: Ensure `CACHE_URL` is correct and Redis is reachable.
- Migrations: Keep DB up to date with `python guest_book/manage.py migrate`.

## License
This project is licensed under the MIT License. See `LICENSE` for details.

---
Production‑ready, extensible Guestbook API. PRs and discussions are welcome.
