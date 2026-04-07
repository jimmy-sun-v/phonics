# Design: Task 1.4 – Create Django App Skeleton – `speech`

## Overview

Generate the `speech` Django app for speech input handling, confidence metrics, and error type tracking.

## Dependencies

- Task 1.1

## Detailed Design

### Directory Structure

```
apps/speech/
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
   mkdir apps\speech
   python manage.py startapp speech apps/speech
   ```

2. **`apps/speech/apps.py`**:
   ```python
   from django.apps import AppConfig

   class SpeechConfig(AppConfig):
       default_auto_field = "django.db.models.BigAutoField"
       name = "apps.speech"
       label = "speech"
       verbose_name = "Speech"
   ```

3. **`apps/speech/urls.py`**:
   ```python
   from django.urls import path

   app_name = "speech"
   urlpatterns = []
   ```

4. **Convert `tests.py` to a package**: Delete `tests.py`, create `tests/__init__.py`.

5. **Empty `models.py`**, `views.py`, `admin.py` with standard imports.

6. **Register in `INSTALLED_APPS`** in `config/settings/base.py`:
   ```python
   "apps.speech",
   ```

7. **Include app URLs in root** `config/urls.py`:
   ```python
   path("api/speech/", include("apps.speech.urls")),
   ```

## Acceptance Criteria

- [ ] `python manage.py check` passes
- [ ] `from apps.speech.models import *` succeeds

## Test Strategy

- `python manage.py check` → 0 issues
