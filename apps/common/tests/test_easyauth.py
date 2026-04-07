import pytest
from django.test import Client, RequestFactory, override_settings
from django.contrib.auth.models import User, AnonymousUser
from apps.common.middleware.easyauth import EasyAuthMiddleware


@pytest.mark.django_db
class TestEasyAuthMiddleware:
    def _get_middleware(self):
        def get_response(request):
            from django.http import HttpResponse
            return HttpResponse("OK")
        return EasyAuthMiddleware(get_response)

    def test_sets_user_from_headers(self):
        middleware = self._get_middleware()
        factory = RequestFactory()
        request = factory.get("/diagnostics/")
        request.META["HTTP_X_MS_CLIENT_PRINCIPAL_NAME"] = "test@example.com"
        request.META["HTTP_X_MS_CLIENT_PRINCIPAL_ID"] = "user-123"

        middleware(request)

        assert request.user.username == "user-123"
        assert request.user.email == "test@example.com"

    def test_creates_user_if_not_exists(self):
        middleware = self._get_middleware()
        factory = RequestFactory()
        request = factory.get("/diagnostics/")
        request.META["HTTP_X_MS_CLIENT_PRINCIPAL_NAME"] = "new@example.com"
        request.META["HTTP_X_MS_CLIENT_PRINCIPAL_ID"] = "new-user-456"

        assert not User.objects.filter(username="new-user-456").exists()
        middleware(request)
        assert User.objects.filter(username="new-user-456").exists()

    @override_settings(EASYAUTH_ENABLED=True)
    def test_redirects_protected_route_when_no_auth(self):
        middleware = self._get_middleware()
        factory = RequestFactory()
        request = factory.get("/diagnostics/")

        response = middleware(request)

        assert response.status_code == 302
        assert "/.auth/login/aad" in response.url

    @override_settings(EASYAUTH_ENABLED=True)
    def test_allows_anonymous_routes(self):
        middleware = self._get_middleware()
        factory = RequestFactory()
        request = factory.get("/phonics/")

        response = middleware(request)

        assert response.status_code == 200

    @override_settings(EASYAUTH_ENABLED=False)
    def test_no_redirect_when_disabled(self):
        middleware = self._get_middleware()
        factory = RequestFactory()
        request = factory.get("/diagnostics/")

        response = middleware(request)

        assert response.status_code == 200

    @override_settings(EASYAUTH_ENABLED=True)
    def test_admin_route_protected(self):
        middleware = self._get_middleware()
        factory = RequestFactory()
        request = factory.get("/admin/")

        response = middleware(request)

        assert response.status_code == 302

    @override_settings(EASYAUTH_ENABLED=True)
    def test_health_check_not_protected(self):
        middleware = self._get_middleware()
        factory = RequestFactory()
        request = factory.get("/health/")

        response = middleware(request)

        assert response.status_code == 200

    @override_settings(EASYAUTH_ENABLED=True)
    def test_api_routes_not_protected(self):
        middleware = self._get_middleware()
        factory = RequestFactory()
        request = factory.get("/api/phonics/categories/")

        response = middleware(request)

        assert response.status_code == 200
