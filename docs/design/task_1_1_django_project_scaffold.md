# Design: Task 1.1 – Initialize Django Project Scaffold

## Overview

Create the Django project with a split-settings configuration, top-level directory layout, and root URL configuration using `config` as the project package name.

## Dependencies

- Task 0.1 (tools installed, venv active)

## Detailed Design

### Directory Structure

```
PhonicsApp/
├── manage.py
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/                 # all Django apps live here
│   └── __init__.py
├── static/
├── templates/
├── docs/
└── scripts/
```

### Step-by-Step Implementation

1. **Create the Django project** using django-admin:
   ```powershell
   django-admin startproject config .
   ```
   This creates `config/` as the project package and `manage.py` in the workspace root.

2. **Convert settings to a package**:
   - Create `config/settings/` directory
   - Move `config/settings.py` → `config/settings/base.py`
   - Create `config/settings/__init__.py` with:
     ```python
     """
     Settings package. Default to dev settings.
     Override with DJANGO_SETTINGS_MODULE env var.
     """
     ```
   - Delete original `config/settings.py`

3. **`config/settings/base.py`** (key sections):
   ```python
   import os
   from pathlib import Path

   BASE_DIR = Path(__file__).resolve().parent.parent.parent

   # SECURITY WARNING: keep the secret key used in production secret!
   SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-change-me-in-production")

   ALLOWED_HOSTS = []

   INSTALLED_APPS = [
       "django.contrib.admin",
       "django.contrib.auth",
       "django.contrib.contenttypes",
       "django.contrib.sessions",
       "django.contrib.messages",
       "django.contrib.staticfiles",
   ]

   MIDDLEWARE = [
       "django.middleware.security.SecurityMiddleware",
       "django.contrib.sessions.middleware.SessionMiddleware",
       "django.middleware.common.CommonMiddleware",
       "django.middleware.csrf.CsrfViewMiddleware",
       "django.contrib.auth.middleware.AuthenticationMiddleware",
       "django.contrib.messages.middleware.MessageMiddleware",
       "django.middleware.clickjacking.XFrameOptionsMiddleware",
   ]

   ROOT_URLCONF = "config.urls"

   TEMPLATES = [
       {
           "BACKEND": "django.template.backends.django.DjangoTemplates",
           "DIRS": [BASE_DIR / "templates"],
           "APP_DIRS": True,
           "OPTIONS": {
               "context_processors": [
                   "django.template.context_processors.debug",
                   "django.template.context_processors.request",
                   "django.contrib.auth.context_processors.auth",
                   "django.contrib.messages.context_processors.messages",
               ],
           },
       },
   ]

   WSGI_APPLICATION = "config.wsgi.application"

   DATABASES = {
       "default": {
           "ENGINE": "django.db.backends.sqlite3",
           "NAME": BASE_DIR / "db.sqlite3",
       }
   }

   LANGUAGE_CODE = "en-us"
   TIME_ZONE = "UTC"
   USE_I18N = True
   USE_TZ = True

   STATIC_URL = "static/"
   STATICFILES_DIRS = [BASE_DIR / "static"]
   STATIC_ROOT = BASE_DIR / "staticfiles"

   DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
   ```

4. **`config/settings/dev.py`**:
   ```python
   from .base import *  # noqa: F401, F403

   DEBUG = True
   ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
   ```

5. **`config/settings/prod.py`**:
   ```python
   from .base import *  # noqa: F401, F403

   DEBUG = False
   # ALLOWED_HOSTS, DATABASES, etc. configured via environment in later tasks
   ```

6. **Update `manage.py`** to default to dev settings:
   ```python
   os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
   ```

7. **Update `config/wsgi.py`** and `config/asgi.py`:
   ```python
   os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
   ```

8. **`config/urls.py`**:
   ```python
   from django.contrib import admin
   from django.urls import path

   urlpatterns = [
       path("admin/", admin.site.urls),
   ]
   ```

9. **Create `apps/` directory** with `__init__.py` for housing all Django apps.

10. **Create empty directories**: `static/`, `templates/`.

### Configuration Notes

- `BASE_DIR` points to the workspace root (`PhonicsApp/`)
- `TEMPLATES.DIRS` includes `BASE_DIR / "templates"` for project-level templates
- `STATICFILES_DIRS` includes `BASE_DIR / "static"` for project-level static files
- SQLite is used as default; PostgreSQL configured in Task 1.8

## Acceptance Criteria

- [x] `python manage.py check` passes with no issues
- [ ] `python manage.py runserver` starts without errors
- [ ] Default Django page renders at `http://localhost:8000`
- [x] Settings split into `base.py`, `dev.py`, `prod.py`
- [x] `DJANGO_SETTINGS_MODULE` defaults to `config.settings.dev`

## Test Strategy

- `python manage.py check` → 0 errors
- `python manage.py runserver` → HTTP 200 at localhost:8000
