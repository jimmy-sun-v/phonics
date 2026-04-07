# Design: Task 1.7 – Configure Environment & Secrets Management

## Overview

Set up environment variable management using `django-environ`. Create `.env.example` documenting all required keys and add `.env` to `.gitignore`.

## Dependencies

- Task 1.1

## Detailed Design

### Files Modified/Created

| File | Action |
|------|--------|
| `config/settings/base.py` | Modify to use `environ` |
| `.env.example` | Create with all keys |
| `.gitignore` | Add `.env` rule |

### Step-by-Step Implementation

1. **Install `django-environ`** (already in `requirements.txt` from Task 0.1):
   ```
   django-environ>=0.11
   ```

2. **Update `config/settings/base.py`** to use `environ`:
   ```python
   import environ
   from pathlib import Path

   BASE_DIR = Path(__file__).resolve().parent.parent.parent

   env = environ.Env(
       DEBUG=(bool, False),
       DJANGO_SECRET_KEY=(str, "django-insecure-change-me-in-production"),
       DATABASE_URL=(str, "sqlite:///db.sqlite3"),
       AZURE_SPEECH_KEY=(str, ""),
       AZURE_SPEECH_REGION=(str, ""),
       AZURE_OPENAI_KEY=(str, ""),
       AZURE_OPENAI_ENDPOINT=(str, ""),
       AZURE_OPENAI_DEPLOYMENT=(str, ""),
       SESSION_RETENTION_HOURS=(int, 24),
   )

   # Read .env file if it exists
   env_file = BASE_DIR / ".env"
   if env_file.exists():
       environ.Env.read_env(str(env_file))

   SECRET_KEY = env("DJANGO_SECRET_KEY")

   # Azure Speech Services
   AZURE_SPEECH_KEY = env("AZURE_SPEECH_KEY")
   AZURE_SPEECH_REGION = env("AZURE_SPEECH_REGION")

   # Azure OpenAI
   AZURE_OPENAI_KEY = env("AZURE_OPENAI_KEY")
   AZURE_OPENAI_ENDPOINT = env("AZURE_OPENAI_ENDPOINT")
   AZURE_OPENAI_DEPLOYMENT = env("AZURE_OPENAI_DEPLOYMENT")

   # Session management
   SESSION_RETENTION_HOURS = env("SESSION_RETENTION_HOURS")
   ```

3. **Create `.env.example`**:
   ```ini
   # Django
   DJANGO_SECRET_KEY=your-secret-key-here
   DEBUG=True

   # Database (PostgreSQL)
   DATABASE_URL=postgres://phonicsapp:password@localhost:5432/phonicsapp_dev

   # Azure Speech Services
   AZURE_SPEECH_KEY=your-azure-speech-key
   AZURE_SPEECH_REGION=eastus

   # Azure OpenAI (via AI Foundry)
   AZURE_OPENAI_KEY=your-azure-openai-key
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

   # Session data retention (hours)
   SESSION_RETENTION_HOURS=24
   ```

4. **Update `.gitignore`** to include:
   ```gitignore
   # Environment
   .env
   .env.local

   # Python
   __pycache__/
   *.py[cod]
   *.egg-info/
   dist/
   build/

   # Virtual environment
   .venv/
   venv/

   # Django
   db.sqlite3
   staticfiles/
   media/

   # IDE
   .vscode/
   .idea/
   *.swp

   # OS
   .DS_Store
   Thumbs.db
   ```

### Security Considerations

- `.env` is **never committed** to version control
- All secrets have empty defaults in `environ.Env()` so the app starts (with warnings) even without `.env`
- Production secrets are set via Azure App Settings (environment variables), not files
- `DJANGO_SECRET_KEY` must be changed from default before any deployment

## Acceptance Criteria

- [ ] `SECRET_KEY` reads from `DJANGO_SECRET_KEY` env var
- [ ] `AZURE_SPEECH_KEY`, `AZURE_OPENAI_KEY` read from env
- [ ] `.env` is in `.gitignore`
- [ ] `.env.example` documents all required keys
- [ ] App starts with `.env` populated from `.env.example` template
- [ ] No hard-coded secrets in settings files

## Test Strategy

- Unit: Verify settings module loads without hard-coded secrets
- Manual: Copy `.env.example` → `.env`, fill values, `runserver` works
