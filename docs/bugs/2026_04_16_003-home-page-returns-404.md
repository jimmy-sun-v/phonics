# BUG 2026_04_16_003: Home Page Returns 404 Instead of Redirecting to Start Page

## Description

Navigating to the root URL (`http://127.0.0.1:8000/`) returns a 404 error. The app's main entry point is `/phonics/` (category selection), but no route is configured for `/`, making the home page inaccessible. Users must know to navigate to `/phonics/` directly.

## Steps to Reproduce

1. Start the dev server: `python manage.py runserver`
2. Open `http://127.0.0.1:8000/` in a browser

## Expected Behavior

The root URL redirects to the phonics category selection page (`/phonics/`).

## Actual Behavior

A 404 "Page not found" error is displayed.

## Fix

**File:** `config/urls.py`

Added a root URL pattern that redirects `/` to the `phonics:category-list-page` named URL (`/phonics/`):

```python
from django.shortcuts import redirect

urlpatterns = [
    path("", lambda request: redirect("phonics:category-list-page")),
    ...
]
```
