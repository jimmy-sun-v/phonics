import logging

from django.http import JsonResponse

logger = logging.getLogger("phonics.security")

MAX_AUDIO_PAYLOAD_BYTES = 5 * 1024 * 1024


class SecurityHeadersMiddleware:
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
                    extra={"path": request.path, "size": content_length},
                )
                return JsonResponse({"error": "Payload too large"}, status=413)

        return self.get_response(request)
