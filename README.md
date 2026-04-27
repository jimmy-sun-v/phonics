# AI Phonics Tutor

A child-safe, AI-assisted phonics learning web application for children aged 5–7, built with Django and deployed on Azure. The app provides structured phonics education through interactive games, speech recognition, and adaptive AI feedback.

## Key Features

- **Structured Learning Flow** — Listen, Observe, Repeat, Practice, Reinforce (each loop < 3 minutes)
- **Speech Interaction** — Azure Speech Services for speech-to-text and text-to-speech with confidence scoring
- **AI Tutoring** — Azure OpenAI provides age-appropriate, encouraging feedback via controlled prompt templates
- **Interactive Games** — Sound-picture matching, beginning sound selection, blend builder, balloon pop
- **Child Safety** — No free-text input, no personal data, no unscripted AI responses, anonymous sessions only
- **Diagnostics Dashboard** — Read-only view for parents and teachers

## Tech Stack

| Layer          | Technology                                      |
| -------------- | ----------------------------------------------- |
| Backend        | Python 3.11+, Django 5.1, Django REST Framework |
| Database       | SQLite (local) / PostgreSQL (production)        |
| Speech         | Azure Cognitive Services Speech SDK             |
| AI             | Azure OpenAI (GPT-4o-mini)                      |
| Infrastructure | Azure App Service, Bicep IaC                    |
| Frontend       | Django templates, server-rendered HTML          |

## Project Structure

```
config/             Django project settings & root URL config
apps/
  phonics/          Phoneme definitions, categories, words & images
  sessions/         Anonymous child sessions, learning progress, attempt history
  speech/           Speech input handling, confidence metrics, TTS service
  ai_tutor/         Prompt templates, LLM response validation, feedback strategies
  games/            Game definitions, game-phonics mappings, story builder
  core/             Shared middleware & sanitization
  common/           Common utilities
templates/          Django HTML templates
static/             CSS, JS, images
infra/              Azure Bicep infrastructure-as-code
docs/               Documentation & design docs
scripts/            Utility scripts
```

## Getting Started

See [docs/getting_started.md](docs/getting_started.md) for full setup instructions. Quick start:

```powershell
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements-dev.txt

# Run migrations (creates tables & seeds phonics data)
python manage.py migrate

# Start the dev server
python manage.py runserver
```

The app runs at **http://127.0.0.1:8000/** with SQLite and no Azure keys required for basic local development.

### Environment Variables

Copy `.env.example` to `.env`. For local development the defaults work out of the box. Azure credentials are optional:

| Variable                  | Purpose                                  |
| ------------------------- | ---------------------------------------- |
| `DJANGO_SECRET_KEY`       | Django secret key                        |
| `DEBUG`                   | Enable debug mode                        |
| `DATABASE_URL`            | Database connection (defaults to SQLite) |
| `AZURE_SPEECH_KEY`        | Azure Speech Services key                |
| `AZURE_SPEECH_REGION`     | Azure Speech Services region             |
| `AZURE_OPENAI_KEY`        | Azure OpenAI key                         |
| `AZURE_OPENAI_ENDPOINT`   | Azure OpenAI endpoint URL                |
| `AZURE_OPENAI_DEPLOYMENT` | Azure OpenAI deployment name             |

## Key URLs

| URL             | Description                           |
| --------------- | ------------------------------------- |
| `/phonics/`     | Category selection — main entry point |
| `/games/`       | Game pages (per phoneme)              |
| `/diagnostics/` | Parent/teacher diagnostics dashboard  |
| `/admin/`       | Django admin (create superuser first) |
| `/health/`      | Health check endpoint                 |

## API Endpoints

| Prefix           | App                      |
| ---------------- | ------------------------ |
| `/api/phonics/`  | Phonics data             |
| `/api/sessions/` | Session management       |
| `/api/speech/`   | Speech recognition & TTS |
| `/api/ai-tutor/` | AI feedback              |
| `/api/games/`    | Game data                |

## Testing

```powershell
pytest
```

Tests live alongside each app in `apps/<app>/tests/`. Configuration is in [pyproject.toml](pyproject.toml) — coverage threshold is 70%.

## Linting & Formatting

```powershell
ruff check .
black --check .
```

## Infrastructure & Deployment

Azure infrastructure is managed with Bicep. See [infra/README.md](infra/README.md) for deployment instructions.

Production startup uses [startup.sh](startup.sh) which runs migrations, collects static files, and starts Gunicorn.

## Documentation

| Document                                                               | Description                     |
| ---------------------------------------------------------------------- | ------------------------------- |
| [docs/getting_started.md](docs/getting_started.md)                     | Setup & run instructions        |
| [docs/requirements/App_Overview.md](docs/requirements/App_Overview.md) | Full application specification  |
| [docs/instruction_breakdown.md](docs/instruction_breakdown.md)         | Task breakdown methodology      |
| [docs/instruction_implement.md](docs/instruction_implement.md)         | Implementation workflow         |
| [docs/design/](docs/design/)                                           | Task design documents           |
| [docs/features/](docs/features/)                                       | Feature specifications          |
| [docs/bugs/](docs/bugs/)                                               | Bug reports & resolutions       |
| [infra/README.md](infra/README.md)                                     | Infrastructure deployment guide |
