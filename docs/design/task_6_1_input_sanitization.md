# Design: Task 6.1 – Input Sanitization & Security Middleware

## Overview

Add security middleware to sanitize all user-facing inputs, enforce CSRF, set security headers, and validate audio payload sizes.

## Dependencies

- Task 1.1 (Django project)

## Detailed Design

### Security Middleware

**File: `apps/core/middleware.py`**

```python
import logging

from django.http import JsonResponse

logger = logging.getLogger("phonics.security")

# Maximum audio payload size: 5 MB
MAX_AUDIO_PAYLOAD_BYTES = 5 * 1024 * 1024


class SecurityHeadersMiddleware:
    """Add security headers to all responses."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Permissions-Policy"] = "microphone=(self), camera=()"
        return response


class AudioPayloadLimitMiddleware:
    """Reject oversized audio payloads on speech endpoints."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.method == "POST"
            and request.path.startswith("/api/speech/")
            and request.content_type == "application/json"
        ):
            content_length = request.META.get("CONTENT_LENGTH")
            if content_length and int(content_length) > MAX_AUDIO_PAYLOAD_BYTES:
                logger.warning(
                    "oversized_payload",
                    extra={
                        "path": request.path,
                        "size": content_length,
                    },
                )
                return JsonResponse(
                    {"error": "Payload too large"},
                    status=413,
                )

        return self.get_response(request)
```

### Input Sanitization Utility

**File: `apps/core/sanitize.py`**

```python
import re


def sanitize_text_input(text: str, max_length: int = 200) -> str:
    """Sanitize text input: strip, truncate, remove control characters."""
    if not isinstance(text, str):
        return ""
    # Remove control characters except newlines and tabs
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = text.strip()
    return text[:max_length]


def sanitize_phoneme_symbol(symbol: str) -> str:
    """Validate phoneme symbol: only lowercase letters, underscores, max 10 chars."""
    if not isinstance(symbol, str):
        return ""
    cleaned = re.sub(r"[^a-z_]", "", symbol.lower())
    return cleaned[:10]
```

### Django Settings Updates

```python
# config/settings/base.py

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "apps.core.middleware.SecurityHeadersMiddleware",
    "apps.core.middleware.AudioPayloadLimitMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "apps.speech.middleware.AttemptLoggingMiddleware",
    ...
]

# Security settings
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
CSRF_COOKIE_HTTPONLY = False  # Needed for JS CSRF token access
SESSION_COOKIE_HTTPONLY = True

# config/settings/prod.py additions
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## Acceptance Criteria

- [ ] Security headers set on all responses
- [ ] Audio payloads > 5MB rejected with 413
- [ ] `sanitize_text_input()` strips control characters and truncates
- [ ] `sanitize_phoneme_symbol()` allows only lowercase + underscore
- [ ] CSRF enforced on all POST endpoints
- [ ] HSTS and SSL redirect in production

## Test Strategy

```python
# tests/test_security.py
import pytest
from apps.core.sanitize import sanitize_text_input, sanitize_phoneme_symbol


class TestSanitizeText:
    def test_strips_control_chars(self):
        assert sanitize_text_input("hello\x00world") == "helloworld"

    def test_truncates(self):
        assert len(sanitize_text_input("a" * 300)) == 200

    def test_strips_whitespace(self):
        assert sanitize_text_input("  hi  ") == "hi"


class TestSanitizeSymbol:
    def test_valid_symbol(self):
        assert sanitize_phoneme_symbol("sh") == "sh"

    def test_rejects_special_chars(self):
        assert sanitize_phoneme_symbol("sh<script>") == "shscript"

    def test_lowercases(self):
        assert sanitize_phoneme_symbol("SH") == "sh"


@pytest.mark.django_db
class TestSecurityHeaders:
    def test_headers_present(self, client):
        resp = client.get("/")
        assert resp["X-Content-Type-Options"] == "nosniff"
        assert resp["X-Frame-Options"] == "DENY"
```
