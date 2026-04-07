# Design: Task 7.1 – Azure App Service Deployment

## Overview

Deploy the Django application to Azure App Service (Linux, Python 3.11). Configure environment variables, static files, database connection, and startup command.

## Dependencies

- Task 7.0 (Bicep IaC — all Azure resources provisioned)
- All previous phases complete

> **Note:** Azure resource provisioning (App Service Plan, Web App, PostgreSQL, etc.) is handled by the Bicep templates in Task 7.0. This task focuses on the **application-level deployment configuration**: startup script, production settings, deployment files, and health check.

## Detailed Design

### Azure Resources (provisioned by Task 7.0)

| Resource | SKU | Purpose |
|----------|-----|---------|
| App Service Plan | B1 (Basic) | Host web app |
| App Service | Linux Python 3.11 | Django application |
| Azure Database for PostgreSQL - Flexible Server | Burstable B1ms | Database |
| Storage Account (optional) | Standard_LRS | Static file CDN |

### Deployment Files

**File: `startup.sh`** (project root)

```bash
#!/bin/bash
set -e

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Seed data (idempotent)
python manage.py seed_phonemes
python manage.py seed_prompts

# Start gunicorn
gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
```

**File: `requirements.txt`** (ensure production deps)

```
django>=5.1,<5.2
djangorestframework>=3.15,<3.16
django-environ>=0.11,<0.12
psycopg2-binary>=2.9,<2.10
gunicorn>=22.0,<23.0
whitenoise>=6.7,<6.8
azure-cognitiveservices-speech>=1.40,<2.0
openai>=1.40,<2.0
```

### Production Settings

**File: `config/settings/prod.py`**

```python
from .base import *

DEBUG = False
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
SECRET_KEY = env("SECRET_KEY")

# Database
DATABASES = {"default": env.db("DATABASE_URL")}

# Static files via WhiteNoise
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

# Security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Logging
LOGGING["handlers"]["file"]["filename"] = "/home/LogFiles/application.log"
```

### Environment Variables (App Service Configuration)

```
DJANGO_SETTINGS_MODULE=config.settings.prod
SECRET_KEY=<generated-secret>
ALLOWED_HOSTS=<app-name>.azurewebsites.net
DATABASE_URL=postgres://<user>:<pass>@<host>:5432/<dbname>?sslmode=require
AZURE_SPEECH_KEY=<from-speech-resource>
AZURE_SPEECH_REGION=<region>
AZURE_OPENAI_ENDPOINT=<endpoint>
AZURE_OPENAI_API_KEY=<key>
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
SESSION_RETENTION_HOURS=24
```

### Deployment Steps

> Steps 1–5 (resource provisioning, startup config, env vars) are now handled by **Task 7.0 (Bicep)**. Only application code deployment remains here.

1. **Deploy Code:**
   ```bash
   az webapp up \
       --name app-phonics-tutor-dev \
       --resource-group rg-phonics-app-dev
   ```

### `.deployment` file (project root)

```ini
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

### Health Check Endpoint

```python
# config/urls.py (add)
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path("health/", health_check),
    ...
]
```

Configure Azure health check: App Service → Health Check → `/health/`

## Acceptance Criteria

- [ ] App deploys and starts on Azure App Service
- [ ] Migrations run automatically on deploy
- [ ] Static files served via WhiteNoise
- [ ] Health check endpoint returns 200
- [ ] All environment variables configured
- [ ] HTTPS enforced with HSTS
- [ ] Logs accessible via App Service log stream

## Test Strategy

- Manual: Deploy → verify `/health/` returns 200
- Manual: Navigate to app → verify pages load
- Manual: Check log stream for startup errors
- Manual: Verify HTTPS redirect
