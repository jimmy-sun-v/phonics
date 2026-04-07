# Design: Task 8.1 – Azure Easy Auth with Microsoft Entra ID

## Overview

Enable Azure App Service built-in authentication ("Easy Auth") with Microsoft Entra ID to protect admin and diagnostics routes, while keeping the main learning app fully anonymous for children.

## Dependencies

- Task 7.1 (Azure App Service deployed)
- Task 5.3 (Diagnostics dashboard)

## Detailed Design

### Authentication Strategy

| Route Pattern | Auth Required | Users |
|---------------|--------------|-------|
| `/`, `/phonics/**`, `/games/**`, `/api/**` | No | Children (anonymous sessions) |
| `/diagnostics/**` | Yes | Parents / teachers |
| `/admin/**` | Yes | Developers / admins |
| `/health/` | No | Azure health probe |

**Key Principle**: Easy Auth is configured with *"Allow unauthenticated requests"* at the platform level. Route-level protection is enforced by Django middleware, giving full control over which paths require login.

### 1. Azure Entra ID App Registration

> **Note:** The Entra ID app registration is a tenant-level operation and cannot be declared in resource-scoped Bicep. It remains a one-time manual/CLI step.

```bash
# Create app registration (one-time)
az ad app create \
    --display-name "Phonics Tutor Auth" \
    --web-redirect-uris "https://<app-name>.azurewebsites.net/.auth/login/aad/callback" \
    --sign-in-audience "AzureADandPersonalMicrosoftAccount"

# Note the appId from output, then create a client secret
az ad app credential reset --id <appId>
```

### 2. Enable Easy Auth on App Service

> **Future improvement:** Easy Auth configuration can be added to `infra/modules/app-service.bicep` via the `Microsoft.Web/sites/config@2023-12-01` (`authsettingsV2`) resource once the Entra ID app registration is created. For now, this remains a CLI step run after the initial Bicep deployment.

```bash
az webapp auth microsoft update \
    --name app-phonics-tutor-dev \
    --resource-group rg-phonics-app-dev \
    --client-id <appId> \
    --client-secret <clientSecret> \
    --issuer "https://login.microsoftonline.com/<tenantId>/v2.0"

# Allow unauthenticated access (children use app without login)
az webapp auth update \
    --name app-phonics-tutor-dev \
    --resource-group rg-phonics-app-dev \
    --unauthenticated-client-action AllowAnonymous \
    --enabled true
```

### 3. Django Easy Auth Middleware

**File: `apps/common/middleware/easyauth.py`**

```python
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import redirect


# Routes that require authentication via Easy Auth
PROTECTED_PREFIXES = ("/diagnostics/", "/admin/")

# Login URL provided by App Service Easy Auth
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
            # Map Easy Auth identity to Django user (create if needed)
            user, _ = User.objects.get_or_create(
                username=principal_id or principal_name,
                defaults={"email": principal_name},
            )
            request.user = user
        else:
            # Check if this is a protected route
            if self._requires_auth(request.path):
                # In production with Easy Auth, redirect to login
                if getattr(settings, "EASYAUTH_ENABLED", False):
                    login_url = EASYAUTH_LOGIN_URL.format(
                        redirect=request.get_full_path()
                    )
                    return redirect(login_url)

        return self.get_response(request)

    def _requires_auth(self, path):
        return any(path.startswith(prefix) for prefix in PROTECTED_PREFIXES)
```

**File: `apps/common/middleware/__init__.py`**

```python
```

**File: `apps/common/__init__.py`**

```python
```

### 4. Settings Changes

**File: `config/settings/base.py`** (add to MIDDLEWARE, after `AuthenticationMiddleware`)

```python
MIDDLEWARE = [
    ...
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.common.middleware.easyauth.EasyAuthMiddleware",
    ...
]

# Easy Auth disabled by default (local dev)
EASYAUTH_ENABLED = False
```

**File: `config/settings/prod.py`** (add)

```python
# Enable Easy Auth route protection in production
EASYAUTH_ENABLED = True
```

### 5. Local Development

In local development, `EASYAUTH_ENABLED = False` means:

- No Easy Auth headers are present → middleware is a no-op
- All routes (including `/diagnostics/`, `/admin/`) are accessible
- Django admin uses its own built-in login (`django.contrib.auth`)
- No external dependencies required for local dev

### 6. Security Considerations

- Easy Auth headers (`X-MS-CLIENT-PRINCIPAL-*`) are **set by the App Service platform** and cannot be spoofed by external clients — the platform strips these headers from incoming requests before injecting its own
- `AllowAnonymous` mode is intentional: children must access the app without login
- The middleware does **not** trust headers in local dev (`EASYAUTH_ENABLED = False`), preventing header injection in non-Azure environments
- Django admin retains its own authentication as a secondary layer

## Acceptance Criteria

- [ ] Entra ID app registration created with correct redirect URIs
- [ ] Easy Auth enabled on App Service with `AllowAnonymous` action
- [ ] `/diagnostics/` and `/admin/` redirect to Microsoft login when unauthenticated (production)
- [ ] Main learning routes remain fully anonymous
- [ ] Authenticated user identity available via `request.user` in protected views
- [ ] Local dev works without Easy Auth (middleware no-op)
- [ ] Middleware unit tests pass

## Test Strategy

- Unit: Middleware sets `request.user` when `X-MS-CLIENT-PRINCIPAL-NAME` header is present
- Unit: Middleware redirects protected routes when `EASYAUTH_ENABLED=True` and no header present
- Unit: Middleware allows anonymous routes regardless of header presence
- Unit: Middleware is no-op when `EASYAUTH_ENABLED=False`
- Integration: Deploy → access `/diagnostics/` → redirected to Microsoft login
- Integration: Deploy → access `/phonics/` → loads without login
- Manual: Sign in via Microsoft → diagnostics dashboard accessible
