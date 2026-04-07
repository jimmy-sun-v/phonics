# Design: Task 1.6 – Create Django App Skeleton – `games`

## Overview

Generate the `games` Django app for game definitions and game-phonics mappings.

## Dependencies

- Task 1.1

## Detailed Design

### Directory Structure

```
apps/games/
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
   mkdir apps\games
   python manage.py startapp games apps/games
   ```

2. **`apps/games/apps.py`**:
   ```python
   from django.apps import AppConfig

   class GamesConfig(AppConfig):
       default_auto_field = "django.db.models.BigAutoField"
       name = "apps.games"
       label = "games"
       verbose_name = "Games"
   ```

3. **`apps/games/urls.py`**:
   ```python
   from django.urls import path

   app_name = "games"
   urlpatterns = []
   ```

4. **Convert `tests.py` to a package**: Delete `tests.py`, create `tests/__init__.py`.

5. **Empty `models.py`**, `views.py`, `admin.py` with standard imports.

6. **Register in `INSTALLED_APPS`** in `config/settings/base.py`:
   ```python
   "apps.games",
   ```

7. **Include app URLs in root** `config/urls.py`:
   ```python
   path("api/games/", include("apps.games.urls")),
   ```

## Acceptance Criteria

- [ ] `python manage.py check` passes
- [ ] `from apps.games.models import *` succeeds

## Test Strategy

- `python manage.py check` → 0 issues
