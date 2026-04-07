# Design: Task 1.3 – Create Django App Skeleton – `sessions`

## Overview

Generate the `sessions` Django app for anonymous child session management. Registered under `apps/sessions/` with a custom label to avoid conflict with Django's built-in `django.contrib.sessions`.

## Dependencies

- Task 1.1

## Detailed Design

### Directory Structure

```
apps/sessions/
├── __init__.py
├── models.py
├── views.py
├── urls.py
├── admin.py
├── apps.py
└── tests/
    └── __init__.py
```

### Step-by-Step Implementation

1. **Create the app**:
   ```powershell
   mkdir apps\sessions
   python manage.py startapp sessions apps/sessions
   ```

2. **`apps/sessions/apps.py`** — Use a distinct label to avoid conflict with Django's built-in sessions app:
   ```python
   from django.apps import AppConfig

   class SessionsConfig(AppConfig):
       default_auto_field = "django.db.models.BigAutoField"
       name = "apps.sessions"
       label = "learning_sessions"
       verbose_name = "Learning Sessions"
   ```
   - **Important**: `label = "learning_sessions"` ensures the DB table prefix is `learning_sessions_` instead of `sessions_`, avoiding collision with `django.contrib.sessions`.

3. **`apps/sessions/urls.py`**:
   ```python
   from django.urls import path

   app_name = "learning_sessions"
   urlpatterns = []
   ```

4. **Convert `tests.py` to a package**: Delete `tests.py`, create `tests/__init__.py`.

5. **Empty `models.py`**, `views.py`, `admin.py` with standard imports.

6. **Register in `INSTALLED_APPS`** in `config/settings/base.py`:
   ```python
   INSTALLED_APPS = [
       # ... Django built-in ...
       # Project apps
       "apps.phonics",
       "apps.sessions",
   ]
   ```

7. **Include app URLs in root** `config/urls.py`:
   ```python
   path("api/sessions/", include("apps.sessions.urls")),
   ```

### Naming Rationale

The Django built-in `django.contrib.sessions` manages HTTP session middleware. Our `apps.sessions` manages **learning sessions** (anonymous child sessions with progress tracking). Using `label = "learning_sessions"` ensures:
- No migration conflicts
- Clear DB table naming: `learning_sessions_learningsession`
- No import confusion

## Acceptance Criteria

- [ ] `python manage.py check` passes
- [ ] No conflict with `django.contrib.sessions`
- [ ] App label is `learning_sessions`
- [ ] `from apps.sessions.models import *` succeeds

## Test Strategy

- `python manage.py check` → 0 issues
- Confirm label: `apps.sessions.apps.SessionsConfig.label == "learning_sessions"`
