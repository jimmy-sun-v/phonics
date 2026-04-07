# Design: Task 5.1 – Attempt Logging Middleware

## Overview

Add structured logging to the speech attempt pipeline so every STT/LLM call, error, and outcome is recorded with timing and context for diagnostics.

## Dependencies

- Task 3.13 (Speech attempt API)

## Detailed Design

### Files

| File | Purpose |
|------|---------|
| `apps/speech/middleware.py` | Request/response logging middleware |
| `apps/speech/logging_config.py` | Logger configuration |

### Logger Setup

**File: `apps/speech/logging_config.py`**

```python
import logging
import time
from functools import wraps

logger = logging.getLogger("phonics.speech")


def log_service_call(service_name: str):
    """Decorator to log service calls with timing."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.monotonic()
            try:
                result = func(*args, **kwargs)
                elapsed = (time.monotonic() - start) * 1000
                logger.info(
                    "service_call",
                    extra={
                        "service": service_name,
                        "function": func.__name__,
                        "duration_ms": round(elapsed, 2),
                        "status": "success",
                    },
                )
                return result
            except Exception as e:
                elapsed = (time.monotonic() - start) * 1000
                logger.error(
                    "service_call_error",
                    extra={
                        "service": service_name,
                        "function": func.__name__,
                        "duration_ms": round(elapsed, 2),
                        "status": "error",
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                    },
                )
                raise
        return wrapper
    return decorator
```

### Apply to Services

Decorate existing service functions:

```python
# apps/speech/services.py
from apps.speech.logging_config import log_service_call

@log_service_call("azure_stt")
def recognize_speech(audio_data: bytes) -> STTResult:
    ...

# apps/ai_tutor/services.py
@log_service_call("azure_llm")
def call_llm(system_prompt: str, user_prompt: str) -> LLMResponse:
    ...
```

### Request Logging Middleware

**File: `apps/speech/middleware.py`**

```python
import logging
import time
import uuid

logger = logging.getLogger("phonics.requests")


class AttemptLoggingMiddleware:
    """Log speech attempt requests with timing and correlation IDs."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith("/api/speech/"):
            return self.get_response(request)

        request_id = str(uuid.uuid4())[:8]
        start = time.monotonic()

        logger.info(
            "attempt_request_start",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.path,
            },
        )

        response = self.get_response(request)

        elapsed = (time.monotonic() - start) * 1000
        logger.info(
            "attempt_request_end",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration_ms": round(elapsed, 2),
            },
        )

        return response
```

### Django Settings

```python
# config/settings/base.py

MIDDLEWARE = [
    ...
    "apps.speech.middleware.AttemptLoggingMiddleware",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "logs/speech_attempts.log",
            "formatter": "json",
        },
    },
    "loggers": {
        "phonics.speech": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
        "phonics.requests": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
    },
}
```

## Acceptance Criteria

- [ ] Every speech API call logged with timing
- [ ] Errors logged with exception type and message
- [ ] Request-level correlation ID in logs
- [ ] Log output to console and file
- [ ] No sensitive data (audio content) in logs

## Test Strategy

```python
# tests/test_logging.py
from unittest.mock import patch
from apps.speech.logging_config import log_service_call


def test_log_service_call_success(caplog):
    @log_service_call("test_service")
    def my_func():
        return "ok"

    with caplog.at_level("INFO", logger="phonics.speech"):
        result = my_func()

    assert result == "ok"
    assert "service_call" in caplog.text


def test_log_service_call_error(caplog):
    @log_service_call("test_service")
    def failing_func():
        raise ValueError("boom")

    with caplog.at_level("ERROR", logger="phonics.speech"):
        try:
            failing_func()
        except ValueError:
            pass

    assert "service_call_error" in caplog.text
```
