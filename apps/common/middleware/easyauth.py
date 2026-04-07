from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import redirect

PROTECTED_PREFIXES = ("/diagnostics/", "/admin/")
EASYAUTH_LOGIN_URL = "/.auth/login/aad?post_login_redirect_uri={redirect}"


class EasyAuthMiddleware:
    """
    Reads Azure App Service Easy Auth headers and maps the
    authenticated identity to Django's request.user.

    When running locally (no Easy Auth), this middleware is a no-op
    and all routes are accessible without authentication.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        principal_name = request.META.get("HTTP_X_MS_CLIENT_PRINCIPAL_NAME")
        principal_id = request.META.get("HTTP_X_MS_CLIENT_PRINCIPAL_ID")

        if principal_name:
            user, _ = User.objects.get_or_create(
                username=principal_id or principal_name,
                defaults={"email": principal_name},
            )
            request.user = user
        else:
            if self._requires_auth(request.path):
                if getattr(settings, "EASYAUTH_ENABLED", False):
                    login_url = EASYAUTH_LOGIN_URL.format(
                        redirect=request.get_full_path()
                    )
                    return redirect(login_url)

        return self.get_response(request)

    def _requires_auth(self, path):
        return any(path.startswith(prefix) for prefix in PROTECTED_PREFIXES)
