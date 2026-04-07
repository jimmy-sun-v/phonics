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
