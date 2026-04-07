# Design: Task 1.2 – Create Django App Skeleton – `phonics`

## Overview

Generate the `phonics` Django app inside `apps/` directory with standard files and register it in `INSTALLED_APPS`.

## Dependencies

- Task 1.1

## Detailed Design

### Directory Structure

```
apps/phonics/
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

1. **Create the app** from the project root:
   ```powershell
   mkdir apps\phonics
   python manage.py startapp phonics apps/phonics
   ```

2. **`apps/phonics/apps.py`**:
   ```python
   from django.apps import AppConfig

   class PhonicsConfig(AppConfig):
       default_auto_field = "django.db.models.BigAutoField"
       name = "apps.phonics"
       label = "phonics"
       verbose_name = "Phonics"
   ```
   - `name` must be `apps.phonics` since the app lives under the `apps/` package.
   - `label` is `phonics` for clean table naming (e.g., `phonics_phoneme`).

3. **`apps/phonics/urls.py`** (empty router):
   ```python
   from django.urls import path

   app_name = "phonics"
   urlpatterns = []
   ```

4. **Convert `tests.py` to a package**:
   - Delete `apps/phonics/tests.py`
   - Create `apps/phonics/tests/__init__.py`

5. **Leave `models.py` empty** (populated in Task 2.1):
   ```python
   from django.db import models
   ```

6. **Leave `views.py` empty**:
   ```python
   # Views will be added in Task 3.11 and Task 4.3
   ```

7. **Leave `admin.py` with default import**:
   ```python
   from django.contrib import admin
   ```

8. **Register in `INSTALLED_APPS`** in `config/settings/base.py`:
   ```python
   INSTALLED_APPS = [
       # Django built-in
       "django.contrib.admin",
       "django.contrib.auth",
       "django.contrib.contenttypes",
       "django.contrib.sessions",
       "django.contrib.messages",
       "django.contrib.staticfiles",
       # Project apps
       "apps.phonics",
   ]
   ```

9. **Include app URLs in root** `config/urls.py`:
   ```python
   from django.urls import path, include

   urlpatterns = [
       path("admin/", admin.site.urls),
       path("api/phonics/", include("apps.phonics.urls")),
   ]
   ```

## Acceptance Criteria

- [ ] `python manage.py check` passes
- [ ] `from apps.phonics.models import *` succeeds
- [ ] `apps.phonics` appears in `INSTALLED_APPS`
- [ ] App label is `phonics` (verified via `AppConfig.label`)

## Test Strategy

- `python manage.py check` → 0 issues
- Python import: `from apps.phonics.models import *` → no error
