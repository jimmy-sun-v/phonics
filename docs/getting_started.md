# Getting Started

How to set up and run the PhonicsApp after cloning the repository.

## Prerequisites

- **Python 3.11+** installed
- **Git** installed

Azure services are optional for local development — the app runs with SQLite and mock-friendly defaults.

## 1. Clone & Enter the Repo

```powershell
git clone <repo-url>
cd PhonicsApp
```

## 2. Create a Virtual Environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
# or: source .venv/bin/activate   # macOS / Linux
```

## 3. Install Dependencies

For **development** (includes test and lint tools):

```powershell
pip install -r requirements-dev.txt
```

For **production only**:

```powershell
pip install -r requirements.txt
```

## 4. Configure Environment Variables

Copy the example file and fill in your values:

```powershell
Copy-Item .env.example .env
```

Edit `.env` with your settings. For local development the defaults work out of the box — the app uses SQLite and no Azure keys are required to start the server:

```dotenv
DJANGO_SECRET_KEY=any-random-string-for-local-dev
DEBUG=True
# DATABASE_URL defaults to sqlite:///db.sqlite3 if omitted
```

If you have Azure credentials, add them:

```dotenv
AZURE_SPEECH_KEY=your-key
AZURE_SPEECH_REGION=eastus
AZURE_OPENAI_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
```

## 5. Run Migrations

This creates the database tables **and** seeds phoneme and prompt template data automatically:

```powershell
python manage.py migrate
```

## 6. Start the Development Server

```powershell
python manage.py runserver
```

The app is now available at **http://127.0.0.1:8000/**.

Key URLs:

| URL | Description |
|-----|-------------|
| `/phonics/` | Category selection — main entry point |
| `/games/` | Game pages (per phoneme) |
| `/diagnostics/` | Parent/teacher diagnostics dashboard |
| `/admin/` | Django admin (create superuser first) |
| `/health/` | Health check endpoint |

### Create a Superuser (optional)

To access the Django admin:

```powershell
python manage.py createsuperuser
```

## 7. Run Tests

```powershell
python -m pytest
```

With coverage:

```powershell
python -m pytest --cov
```

## 8. Lint & Format

```powershell
ruff check .          # lint
ruff check . --fix    # auto-fix lint issues
black .               # format
```

## Management Commands

### Purge Expired Sessions

Remove learning sessions older than the retention period (default: 24 hours):

```powershell
python manage.py purge_expired_sessions
```

Options:

- `--hours N` — override retention period
- `--dry-run` — preview without deleting

## Project Structure

```
PhonicsApp/
├── config/              # Django project settings & root URL config
│   └── settings/
│       ├── base.py      # Shared settings
│       ├── dev.py       # Local development overrides
│       └── prod.py      # Production overrides
├── apps/
│   ├── phonics/         # Phoneme models, API, learning loop pages
│   ├── sessions/        # Anonymous learning sessions & progress
│   ├── speech/          # STT, TTS, error detection, diagnostics
│   ├── ai_tutor/        # LLM client, prompt templates, safety
│   ├── games/           # Game models, API, game pages
│   ├── core/            # Security middleware
│   └── common/          # Shared utilities (Easy Auth middleware)
├── templates/           # Django templates
├── static/              # CSS, JS, images
├── infra/               # Azure Bicep IaC
└── docs/                # Design documents
```

## Production Deployment

See [task_7_1_azure_deployment.md](design/task_7_1_azure_deployment.md) for Azure App Service deployment instructions. The `startup.sh` script handles migrations, static file collection, and Gunicorn startup.
