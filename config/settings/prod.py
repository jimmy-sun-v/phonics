from .base import *  # noqa: F401, F403

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
