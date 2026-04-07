# Design: Task 1.5 – Create Django App Skeleton – `ai_tutor`

## Overview

Generate the `ai_tutor` Django app for prompt templates, LLM response validation, and feedback strategies. Includes a `prompts/` subdirectory for prompt template files.

## Dependencies

- Task 1.1

## Detailed Design

### Directory Structure

```
apps/ai_tutor/
├── __init__.py
├── models.py
├── views.py
├── urls.py
├── admin.py
├── apps.py
├── prompts/           # prompt template text files (if file-based)
│   └── .gitkeep
└── tests/
    └── __init__.py
```

### Step-by-Step Implementation

1. **Create the app**:
   ```powershell
   mkdir apps\ai_tutor
   python manage.py startapp ai_tutor apps/ai_tutor
   ```

2. **`apps/ai_tutor/apps.py`**:
   ```python
   from django.apps import AppConfig

   class AiTutorConfig(AppConfig):
       default_auto_field = "django.db.models.BigAutoField"
       name = "apps.ai_tutor"
       label = "ai_tutor"
       verbose_name = "AI Tutor"
   ```

3. **`apps/ai_tutor/urls.py`**:
   ```python
   from django.urls import path

   app_name = "ai_tutor"
   urlpatterns = []
   ```

4. **Convert `tests.py` to a package**: Delete `tests.py`, create `tests/__init__.py`.

5. **Create `apps/ai_tutor/prompts/`** directory with `.gitkeep`.

6. **Empty `models.py`**, `views.py`, `admin.py` with standard imports.

7. **Register in `INSTALLED_APPS`** in `config/settings/base.py`:
   ```python
   "apps.ai_tutor",
   ```

8. **Include app URLs in root** `config/urls.py`:
   ```python
   path("api/ai-tutor/", include("apps.ai_tutor.urls")),
   ```

## Acceptance Criteria

- [ ] `python manage.py check` passes
- [ ] `from apps.ai_tutor.models import *` succeeds
- [ ] `prompts/` directory exists

## Test Strategy

- `python manage.py check` → 0 issues
