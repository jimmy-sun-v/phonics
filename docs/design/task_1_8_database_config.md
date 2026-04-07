# Design: Task 1.8 – Configure Database Connection (PostgreSQL)

## Overview

Configure Django to connect to PostgreSQL using the `DATABASE_URL` environment variable via `django-environ`. SQLite remains as fallback for quick local dev.

## Dependencies

- Task 1.7 (environment config with `django-environ`)

## Detailed Design

### Files Modified

| File | Action |
|------|--------|
| `config/settings/base.py` | Update DATABASES to use `DATABASE_URL` |
| `config/settings/dev.py` | Add dev-specific DB settings |
| `config/settings/prod.py` | Add prod-specific DB settings |

### Step-by-Step Implementation

1. **Ensure `psycopg2-binary`** is in `requirements.txt` (added in Task 0.1):
   ```
   psycopg2-binary>=2.9
   ```

2. **Update `config/settings/base.py`** — replace static DATABASES with environ:
   ```python
   DATABASES = {
       "default": env.db(
           "DATABASE_URL",
           default="sqlite:///db.sqlite3",
       )
   }
   ```
   `env.db()` parses the `DATABASE_URL` string into Django's DATABASES dict format automatically:
   - `postgres://user:pass@host:port/dbname` → PostgreSQL config
   - `sqlite:///db.sqlite3` → SQLite fallback

3. **`config/settings/dev.py`** — dev overrides:
   ```python
   from .base import *  # noqa: F401, F403

   DEBUG = True
   ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

   # Dev can use SQLite if DATABASE_URL not set
   # No additional DB config needed; base.py handles the default
   ```

4. **`config/settings/prod.py`** — production overrides:
   ```python
   from .base import *  # noqa: F401, F403

   DEBUG = False
   # DATABASE_URL must be set in Azure App Settings
   # SSL is typically handled by the connection string options:
   #   postgres://user:pass@host:5432/db?sslmode=require
   ```

5. **`.env` for local dev** (from `.env.example`):
   ```ini
   DATABASE_URL=postgres://phonicsapp:password@localhost:5432/phonicsapp_dev
   ```

### PostgreSQL Setup (Local Dev)

```sql
-- Run in psql as superuser:
CREATE DATABASE phonicsapp_dev;
CREATE USER phonicsapp WITH PASSWORD 'password';
ALTER ROLE phonicsapp SET client_encoding TO 'utf8';
ALTER ROLE phonicsapp SET default_transaction_isolation TO 'read committed';
ALTER ROLE phonicsapp SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE phonicsapp_dev TO phonicsapp;
-- For PostgreSQL 15+, also grant schema permissions:
\c phonicsapp_dev
GRANT ALL ON SCHEMA public TO phonicsapp;
```

### Verification Steps

```powershell
# Apply migrations
python manage.py migrate

# Verify all migrations applied
python manage.py showmigrations

# Quick check
python manage.py check --database default
```

## Acceptance Criteria

- [ ] `python manage.py migrate` completes without error against PostgreSQL
- [ ] Default Django tables created in PostgreSQL
- [ ] `showmigrations` shows all applied
- [ ] Falls back to SQLite if `DATABASE_URL` not set
- [ ] No database credentials in source code

## Test Strategy

- Integration: `manage.py migrate` + `showmigrations` shows all applied
- Unit: Settings resolve `DATABASES` from `DATABASE_URL` env var
