## Guestbook API

A simple, production-minded Django REST API for a guestbook. It lets visitors leave entries and provides a summarized user list.

### Running with Docker (Quickstart)
1. Copy env template and adjust if needed:
   ```bash
   cp env.example .env
   ```
2. Build and start:
   ```bash
   docker compose up --build -d
   ```
3. App is available at `http://127.0.0.1/` (Nginx proxy) and directly at `http://127.0.0.1:8000` (Gunicorn).
   - Static files are collected to `guest_book/guest_book/staticfiles` and served by Nginx at `/static/`.

4. Run migrations:
   ```bash
   docker compose exec web python guest_book/manage.py migrate
   ```
5. Create a superuser (non-interactive):
   ```bash
   docker compose exec -e DJANGO_SUPERUSER_USERNAME=admin \
                       -e DJANGO_SUPERUSER_EMAIL=admin@example.com \
                       -e DJANGO_SUPERUSER_PASSWORD=admin123 \
                       web python guest_book/manage.py createsuperuser --noinput
   ```
6. (Optional) Generate fake data:
   ```bash
   docker compose exec web python guest_book/manage.py generate_fake_data --users 200 --entries 1000
   ```
7. Open Admin UI: `http://localhost/admin/` (via Nginx)

8. API Docs:
   - Swagger UI: `http://127.0.0.1/api/docs/`
   - OpenAPI schema: `http://127.0.0.1/api/schema/`

Common commands:
```bash
# View logs
docker compose logs -f web

# Run management commands
docker compose exec web python guest_book/manage.py migrate
docker compose exec web python guest_book/manage.py generate_fake_data --users 200 --entries 1000
```

### API Overview
Base URL prefix: `/api/v1`

- **Entries**
  - `POST /api/v1/entries`
    - Body:
      ```json
      { "name": "John Doe", "subject": "Hello", "message": "Nice place!" }
      ```
    - Creates an entry. The `name` is normalized (locale-aware Turkish mapping) and a `User` is created if missing.
  - `GET /api/v1/entries`
    - Paginated list. Response shape:
      ```json
      {
        "count": 123,
        "page_size": 3,
        "total_pages": 41,
        "current_page_number": 1,
        "links": { "next": "...", "previous": null },
        "entries": [
          { "user": "John Doe", "subject": "Hello", "message": "Nice place!" }
        ]
      }
      ```
    - Notes: `count` is cached for 30s; immediate consistency is not guaranteed.

- **Users**
  - `GET /api/v1/users`
    - Returns:
      ```json
      {
        "users": [
          { "username": "John Doe", "total_entries": 12, "last_entry": "Subject | Message" }
        ]
      }
      ```
    - Notes: Response cached for 30s. If strict freshness is required, replace caching with pagination.

### Implementation Notes
- Models:
  - `user.User` with custom queryset `with_entry_summary()` that annotates `total_entries` and `last_entry` using subqueries.
  - `entry.Entry` extends `TimestampedModel` and indexes `(user, -created_date)` for fast last-entry lookups.
- Pagination:
  - `EntryPagination` returns a compact envelope and caches total count (TTL 30s).
- Normalization:
  - `libs.normalize.turkish_str` provides locale-aware title-casing for Turkish-specific characters.

### Development Tips
- Use `django-extensions` (`shell_plus`) for quicker interactive work.
- Keep `DEBUG=True` only for local development.

### License
MIT (or specify your actual license).

---

### Local Development (without Docker)
- Requirements:
  - Python >= 3.10
  - PostgreSQL (default: `localhost:5432`)
  - Redis (default: `redis://127.0.0.1:6379/1`)

Steps:
1. Create virtualenv and install deps
   ```bash
   uv sync
   # or
   pip install -r requirements.txt
   ```
2. Configure environment (optional): edit `.env` or export variables
3. Run migrations and start server
   ```bash
   python guest_book/manage.py migrate
   python guest_book/manage.py runserver
   ```
4. Swagger UI (local dev): `http://127.0.0.1:8000/api/docs/`
