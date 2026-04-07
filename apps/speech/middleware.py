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
