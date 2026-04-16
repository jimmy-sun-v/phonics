# BUG 2026_04_16_004: /games/ Path Returns 404

## Description

Navigating to `/games/` returns a 404 error. The games URL configuration only defines routes with game type and phoneme symbol parameters (e.g., `/games/sound_picture/sh/`), with no root route for `/games/` itself. Users who navigate to `/games/` directly see a "Page not found" error.

## Steps to Reproduce

1. Start the dev server: `python manage.py runserver`
2. Open `http://127.0.0.1:8000/games/` in a browser

## Expected Behavior

The `/games/` URL should redirect to the phonics category selection page (`/phonics/`), since games are accessed per-phoneme from the learning flow.

## Actual Behavior

A 404 "Page not found" error is displayed.

## Fix

**File:** `config/urls.py`

Added a catch-all URL pattern at the end of `urlpatterns` and a custom 404 handler in `config/urls.py`:

```python
from django.urls import include, path, re_path

def custom_404(request, exception):
    return redirect("phonics:category-list-page")

urlpatterns = [
    # ... existing routes ...
    # Catch-all: redirect any unmatched URL to the start page
    re_path(r"^.*$", lambda request: redirect("phonics:category-list-page")),
]

handler404 = custom_404
```

The `re_path` catch-all works in both `DEBUG=True` and `DEBUG=False` modes. The `handler404` is kept as a production fallback. The initial fix of adding a `games_index_view` redirect in `apps/games/page_urls.py` and `page_views.py` was reverted since the catch-all makes it redundant.

---

## Follow-up: Redundant Navigation Buttons

### Issue

After fixing `/` and `/games/` to both redirect to `/phonics/`, the bottom navigation bar in `templates/base.html` had three buttons — Home, Learn, and Games — that all navigated to the same destination (`/phonics/`). This is confusing and unnecessary.

### Root Cause

The nav bar was designed before the redirects were added. The Home (`/`) and Games (`/games/`) buttons originally assumed those paths would have their own content, but since games are accessed per-phoneme from the learning flow and the root URL redirects to phonics, all three buttons are functionally identical.

### Fix

Removed the Home and Games buttons from the nav bar in `templates/base.html`, keeping only the Learn button (`/phonics/`). The `{% block nav %}` still allows individual templates to override navigation if needed.

---

## Follow-up: Graceful Redirect for All Invalid URLs

### Issue

The fixes for `/` and `/games/` only handle those specific paths. Any other manually typed invalid URL (e.g., `/about/`, `/help/`, `/foo/`) still shows Django's default 404 "Page not found" error page, which is not user-friendly for a children's app.

### Root Cause

Django's default 404 handler renders a generic error page. There is no catch-all mechanism to redirect users to a known-good page when they navigate to an unrecognized URL.

### Fix

Added a catch-all `re_path` at the end of `urlpatterns` in `config/urls.py`:

```python
re_path(r"^.*$", lambda request: redirect("phonics:category-list-page")),
```

This sits after all valid routes and redirects any unmatched URL to `/phonics/`. Unlike `handler404` alone, the catch-all works in both `DEBUG=True` and `DEBUG=False` modes, so developers and end users both get the redirect.
