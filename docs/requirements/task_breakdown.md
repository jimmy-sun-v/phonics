# AI Phonics Tutor – Task Breakdown

> Derived from [App_Overview.md](requirements/App_Overview.md) following the structure defined in [instruction_breakdown.md](instruction_breakdown.md).

---

## Phase 1 – Foundations & Configuration

---

### Task 1.1: Initialize Django Project Scaffold

**Description**
Create the Django project with the top-level directory layout, `manage.py`, project settings module, and root URL configuration.

**Dependencies**
None

**Inputs / Outputs**

- Input: None
- Output: Runnable Django project skeleton responding to `manage.py runserver`

**Acceptance Criteria**

- `manage.py runserver` starts without errors
- Default Django welcome page renders at `http://localhost:8000`
- Project uses Python 3.11+

**Test Strategy**

- Unit: `python manage.py check` passes with no issues
- Manual: `runserver` → browser shows Django default page

**Target Folder(s)**

```
PhonicsApp/
├── manage.py
├── config/          # project settings package
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   └── wsgi.py
```

---

### Task 1.2: Create Django App Skeleton – `phonics`

**Description**
Generate the `phonics` Django app with empty `models.py`, `views.py`, `urls.py`, `admin.py`, and `tests/` package. Register it in `INSTALLED_APPS`.

**Dependencies**
Task 1.1

**Inputs / Outputs**

- Input: Django project from Task 1.1
- Output: `phonics` app registered and importable

**Acceptance Criteria**

- `python manage.py check` passes
- `from phonics.models import *` succeeds (empty)

**Test Strategy**

- Unit: `manage.py check` passes
- Unit: App appears in `INSTALLED_APPS`

**Target Folder(s)**

```
PhonicsApp/apps/phonics/
├── __init__.py
├── models.py
├── views.py
├── urls.py
├── admin.py
├── apps.py
└── tests/
    └── __init__.py
```

---

### Task 1.3: Create Django App Skeleton – `sessions`

**Description**
Generate the `sessions` Django app for anonymous child session management.

**Dependencies**
Task 1.1

**Inputs / Outputs**

- Input: Django project from Task 1.1
- Output: `sessions` app registered and importable

**Acceptance Criteria**

- `python manage.py check` passes

**Test Strategy**

- Unit: `manage.py check` passes

**Target Folder(s)**

```
PhonicsApp/apps/sessions/
├── __init__.py
├── models.py
├── views.py
├── urls.py
├── admin.py
├── apps.py
└── tests/
    └── __init__.py
```

---

### Task 1.4: Create Django App Skeleton – `speech`

**Description**
Generate the `speech` Django app for speech input handling, confidence metrics, and error types.

**Dependencies**
Task 1.1

**Inputs / Outputs**

- Input: Django project from Task 1.1
- Output: `speech` app registered and importable

**Acceptance Criteria**

- `python manage.py check` passes

**Test Strategy**

- Unit: `manage.py check` passes

**Target Folder(s)**

```
PhonicsApp/apps/speech/
├── __init__.py
├── models.py
├── views.py
├── urls.py
├── admin.py
├── apps.py
└── tests/
    └── __init__.py
```

---

### Task 1.5: Create Django App Skeleton – `ai_tutor`

**Description**
Generate the `ai_tutor` Django app for prompt templates, LLM response validation, and feedback strategies.

**Dependencies**
Task 1.1

**Inputs / Outputs**

- Input: Django project from Task 1.1
- Output: `ai_tutor` app registered and importable

**Acceptance Criteria**

- `python manage.py check` passes

**Test Strategy**

- Unit: `manage.py check` passes

**Target Folder(s)**

```
PhonicsApp/apps/ai_tutor/
├── __init__.py
├── models.py
├── views.py
├── urls.py
├── admin.py
├── apps.py
├── prompts/          # prompt template files
└── tests/
    └── __init__.py
```

---

### Task 1.6: Create Django App Skeleton – `games`

**Description**
Generate the `games` Django app for game definitions and game–phonics mappings.

**Dependencies**
Task 1.1

**Inputs / Outputs**

- Input: Django project from Task 1.1
- Output: `games` app registered and importable

**Acceptance Criteria**

- `python manage.py check` passes

**Test Strategy**

- Unit: `manage.py check` passes

**Target Folder(s)**

```
PhonicsApp/apps/games/
├── __init__.py
├── models.py
├── views.py
├── urls.py
├── admin.py
├── apps.py
└── tests/
    └── __init__.py
```

---

### Task 1.7: Configure Environment & Secrets Management

**Description**
Set up `django-environ` (or equivalent) for environment variable management. Create `.env.example` with all required keys (database URL, Azure Speech key, Azure OpenAI key, Django secret key). Add `.env` to `.gitignore`.

**Dependencies**
Task 1.1

**Inputs / Outputs**

- Input: Project settings
- Output: Settings load from environment; `.env.example` documents all keys

**Acceptance Criteria**

- `SECRET_KEY`, `DATABASE_URL`, `AZURE_SPEECH_KEY`, `AZURE_OPENAI_KEY` read from env
- `.env` is gitignored
- App starts with `.env` populated from `.env.example`

**Test Strategy**

- Unit: Settings module loads without hard-coded secrets
- Manual: Copy `.env.example` → `.env`, fill values, confirm `runserver` works

**Target Folder(s)**

```
PhonicsApp/
├── .env.example
├── .gitignore
└── config/settings/base.py
```

---

### Task 1.8: Configure Database Connection (PostgreSQL)

**Description**
Configure Django to connect to PostgreSQL (local dev) or Azure SQL/PostgreSQL (prod) using the `DATABASE_URL` environment variable.

**Dependencies**
Task 1.7

**Inputs / Outputs**

- Input: `DATABASE_URL` env var
- Output: Django connects to Postgres; `migrate` runs cleanly

**Acceptance Criteria**

- `python manage.py migrate` completes without error
- Default tables created in PostgreSQL

**Test Strategy**

- Integration: `migrate` + `showmigrations` shows all applied
- Unit: settings resolve `DATABASES` from `DATABASE_URL`

**Target Folder(s)**

```
config/settings/base.py
config/settings/dev.py
```

---

### Task 1.9: Set Up Static Files & Base Template Structure

**Description**
Configure Django static file handling (`STATICFILES_DIRS`, `STATIC_URL`). Create a base HTML template with responsive `<meta viewport>`, CSS reset, and placeholder blocks.

**Dependencies**
Task 1.1

**Inputs / Outputs**

- Input: Django project
- Output: `base.html` with responsive layout, static files served in dev

**Acceptance Criteria**

- `{% static %}` tag resolves correctly
- `base.html` contains `<meta name="viewport" ...>`
- Page renders correctly on desktop (≥1024px), tablet (768–1023px), mobile (<768px)

**Test Strategy**

- Manual: Load page at 3 viewport widths, confirm no horizontal overflow
- Unit: Template renders without errors via `TemplateResponse`

**Target Folder(s)**

```
PhonicsApp/
├── static/
│   ├── css/
│   │   └── base.css
│   ├── js/
│   └── images/
└── templates/
    └── base.html
```

---

### Task 1.10: Add Development Tooling (Linting, Formatting, Requirements)

**Description**
Add `requirements.txt` (or `pyproject.toml`), configure `ruff` or `flake8` for linting, `black` for formatting, and `pytest-django` for testing.

**Dependencies**
Task 1.1

**Inputs / Outputs**

- Input: Project root
- Output: `pip install -r requirements.txt` succeeds; lint/format/test commands work

**Acceptance Criteria**

- `ruff check .` or `flake8` runs cleanly
- `pytest` discovers and runs tests (0 tests initially)
- All project dependencies pinned

**Test Strategy**

- Manual: Run `pip install -r requirements.txt && pytest && ruff check .`

**Target Folder(s)**

```
PhonicsApp/
├── requirements.txt (or pyproject.toml)
├── pytest.ini (or pyproject.toml section)
└── ruff.toml (or pyproject.toml section)
```

---

## Phase 2 – Data Models & Core Services

---

### Task 2.1: Phoneme Model & Migration

**Description**
Define the `Phoneme` model with fields: `symbol` (CharField), `category` (CharField with choices: single_letter, digraph, blend, long_vowel, r_controlled, diphthong), `example_words` (JSONField), `audio_file` (FileField, optional), `display_order` (IntegerField).

**Dependencies**
Task 1.2, Task 1.8

**Inputs / Outputs**

- Input: Database connection
- Output: `phonics_phoneme` table created

**Acceptance Criteria**

- Migration generated and applied cleanly
- `Phoneme.objects.create(symbol="sh", category="digraph", example_words=["ship","shop"])` succeeds
- Admin interface shows Phoneme list

**Test Strategy**

- Unit: Create, read, update, delete a `Phoneme` instance
- Unit: Validate category choices reject invalid values

**Target Folder(s)**

```
apps/phonics/models.py
apps/phonics/admin.py
apps/phonics/migrations/
```

---

### Task 2.2: Phonics Seed Data – All Categories

**Description**
Create a Django data migration (or management command) that seeds **all** phoneme categories from the overview: single letter sounds (consonants + short vowels), digraphs, blends, long vowel patterns, R-controlled vowels, diphthongs. Include 2–3 example words per phoneme.

**Dependencies**
Task 2.1

**Inputs / Outputs**

- Input: Phoneme model
- Output: Database populated with complete phonics dataset

**Acceptance Criteria**

- All phoneme symbols from App_Overview §3.1.1 are present
- Each phoneme has category, example_words (≥2 words)
- Running the seed is idempotent (re-runnable without duplicates)
- Phonics data is data-driven, not hard-coded in application logic

**Test Strategy**

- Unit: Count phonemes per category matches expected counts
- Unit: Verify specific phonemes exist (e.g., `sh`, `ch`, `a_e`, `ar`, `oi`)
- Integration: `manage.py migrate` applies seed data correctly

**Target Folder(s)**

```
apps/phonics/migrations/  (data migration)
  OR
apps/phonics/management/commands/seed_phonics.py
apps/phonics/data/phonemes.json   (source data file)
```

---

### Task 2.3: LearningSession Model & Migration

**Description**
Define the `LearningSession` model: `session_id` (UUIDField, primary key, auto-generated), `current_phoneme` (FK → Phoneme, nullable), `started_at` (DateTimeField, auto_now_add), `last_active_at` (DateTimeField, auto_now), `is_active` (BooleanField, default True).

**Dependencies**
Task 2.1

**Inputs / Outputs**

- Input: Phoneme model exists
- Output: `sessions_learningsession` table

**Acceptance Criteria**

- Session can be created with auto-generated UUID
- FK to Phoneme works correctly
- `last_active_at` updates on save

**Test Strategy**

- Unit: Create session, verify UUID auto-generated
- Unit: Assign phoneme FK, save, read back
- Unit: Verify `last_active_at` changes on update

**Target Folder(s)**

```
apps/sessions/models.py
apps/sessions/admin.py
apps/sessions/migrations/
```

---

### Task 2.4: SpeechAttempt Model & Migration

**Description**
Define the `SpeechAttempt` model: `session` (FK → LearningSession), `phoneme` (FK → Phoneme), `confidence` (FloatField), `detected_error` (CharField, blank/null), `attempt_number` (PositiveIntegerField), `created_at` (DateTimeField, auto_now_add).

**Dependencies**
Task 2.1, Task 2.3

**Inputs / Outputs**

- Input: Phoneme and LearningSession models
- Output: `speech_speechattempt` table

**Acceptance Criteria**

- Speech attempt linked to a session and phoneme
- Confidence stored as float (0.0–1.0)
- Attempt number is a positive integer

**Test Strategy**

- Unit: CRUD operations on SpeechAttempt
- Unit: Validate confidence range via model validation
- Unit: FK cascade behavior on session/phoneme deletion

**Target Folder(s)**

```
apps/speech/models.py
apps/speech/admin.py
apps/speech/migrations/
```

---

### Task 2.5: Game & GamePhonemeMapping Models

**Description**
Define `Game` model: `name` (CharField), `game_type` (CharField with choices: sound_picture, beginning_sound, blend_builder, balloon_pop), `description` (TextField), `is_active` (BooleanField). Define `GamePhonemeMapping` model: `game` (FK → Game), `phoneme` (FK → Phoneme). Add unique constraint on (game, phoneme).

**Dependencies**
Task 2.1

**Inputs / Outputs**

- Input: Phoneme model
- Output: `games_game` and `games_gamephonememapping` tables

**Acceptance Criteria**

- 4 game types defined as choices
- Each game can be linked to multiple phonemes
- Duplicate (game, phoneme) pairs rejected

**Test Strategy**

- Unit: Create all 4 game types
- Unit: Map phoneme to game, verify reverse lookup
- Unit: Duplicate mapping raises `IntegrityError`

**Target Folder(s)**

```
apps/games/models.py
apps/games/admin.py
apps/games/migrations/
```

---

### Task 2.6: PromptTemplate Model & Migration

**Description**
Define `PromptTemplate` model in `ai_tutor`: `name` (CharField, unique), `system_prompt` (TextField), `user_template` (TextField with placeholders like `{phoneme}`, `{confidence}`, `{error}`, `{attempts}`), `is_active` (BooleanField), `version` (PositiveIntegerField).

**Dependencies**
Task 1.5

**Inputs / Outputs**

- Input: ai_tutor app
- Output: `ai_tutor_prompttemplate` table

**Acceptance Criteria**

- Template can be created with placeholder syntax
- `user_template.format(phoneme="/sh/", confidence=0.61, error="/s/", attempts=3)` works
- Only one active template per name (enforced at service layer)

**Test Strategy**

- Unit: CRUD operations on PromptTemplate
- Unit: Template string formatting with sample context succeeds
- Unit: Unique name constraint

**Target Folder(s)**

```
apps/ai_tutor/models.py
apps/ai_tutor/admin.py
apps/ai_tutor/migrations/
```

---

### Task 2.7: Seed Default AI Prompt Templates

**Description**
Create a data migration or management command to seed the default prompt template from App_Overview §8 (system prompt for child-safe phonics tutor + user context template).

**Dependencies**
Task 2.6

**Inputs / Outputs**

- Input: PromptTemplate model
- Output: Default prompt template in database

**Acceptance Criteria**

- System prompt includes rules: simple words, encouraging, no "wrong", no personal questions, 1-2 sentences
- User template accepts `{phoneme}`, `{confidence}`, `{error}`, `{attempts}`
- Seed is idempotent

**Test Strategy**

- Unit: Template exists after migration
- Unit: Template content matches safety constraints
- Integration: `manage.py migrate` applies without error

**Target Folder(s)**

```
apps/ai_tutor/migrations/
apps/ai_tutor/data/default_prompts.json
```

---

### Task 2.8: Session Data Expiry Service

**Description**
Implement a service/management command to purge sessions older than a configurable threshold (default: 24 hours). Sessions with `last_active_at` older than the threshold and their related `SpeechAttempt` records are soft-deleted or hard-deleted.

**Dependencies**
Task 2.3, Task 2.4

**Inputs / Outputs**

- Input: Configurable retention period (env var `SESSION_RETENTION_HOURS`, default 24)
- Output: Expired sessions and related attempts removed

**Acceptance Criteria**

- Sessions older than threshold are deleted
- Related SpeechAttempts cascade-deleted
- Sessions within threshold are untouched
- Retention period is configurable

**Test Strategy**

- Unit: Create sessions with past timestamps, run purge, verify deletion
- Unit: Recent sessions survive purge
- Unit: Configurable threshold changes behavior

**Target Folder(s)**

```
apps/sessions/services.py
apps/sessions/management/commands/purge_expired_sessions.py
apps/sessions/tests/
```

---

## Phase 3 – APIs & Business Logic

---

### Task 3.1: Phonics Engine Service

**Description**
Create a service layer in `phonics` that provides: `get_all_categories()`, `get_phonemes_by_category(category)`, `get_phoneme_detail(symbol)`, `get_next_phoneme(session)` (returns the next phoneme in learning sequence).

**Dependencies**
Task 2.1, Task 2.2

**Inputs / Outputs**

- Input: Phoneme data in database
- Output: Structured phoneme data (dicts/dataclasses)

**Acceptance Criteria**

- All 6 categories retrievable
- Phonemes returned in `display_order`
- `get_next_phoneme` returns a phoneme the session hasn't completed yet

**Test Strategy**

- Unit: `get_all_categories()` returns 6 categories
- Unit: `get_phonemes_by_category("digraph")` returns `ch, sh, th, wh, ph, ng, kn, wr`
- Unit: `get_next_phoneme` skips already-completed phonemes

**Target Folder(s)**

```
apps/phonics/services.py
apps/phonics/tests/test_services.py
```

---

### Task 3.2: Session Management Service

**Description**
Create a service that handles: `create_session()` → returns new anonymous session with UUID, `get_session(session_id)`, `update_current_phoneme(session_id, phoneme)`, `deactivate_session(session_id)`.

**Dependencies**
Task 2.3

**Inputs / Outputs**

- Input: Session ID (UUID)
- Output: LearningSession instances

**Acceptance Criteria**

- New session created with auto-generated UUID (no PII)
- Session retrieval by UUID works
- Phoneme can be updated on active session
- Deactivated sessions cannot be updated

**Test Strategy**

- Unit: Create session, verify UUID format
- Unit: Update phoneme, read back
- Unit: Deactivate session, attempt update → fails gracefully

**Target Folder(s)**

```
apps/sessions/services.py
apps/sessions/tests/test_services.py
```

---

### Task 3.3: Progress Tracking Service

**Description**
Create a service to track learning progress per session: `record_attempt(session_id, phoneme_symbol, confidence, error)`, `get_progress(session_id)` → returns completed/in-progress/remaining phonemes, `get_attempts_for_phoneme(session_id, phoneme_symbol)`.

**Dependencies**
Task 2.3, Task 2.4, Task 3.1

**Inputs / Outputs**

- Input: Session ID, attempt data
- Output: Progress summary, attempt history

**Acceptance Criteria**

- Attempt recorded with incrementing `attempt_number`
- Progress shows correct counts of completed/remaining
- A phoneme is "completed" when confidence ≥ threshold (configurable, default 0.7)

**Test Strategy**

- Unit: Record 3 attempts, verify `attempt_number` = 1, 2, 3
- Unit: Phoneme with confidence ≥ 0.7 marked complete
- Unit: Progress summary counts match expectations

**Target Folder(s)**

```
apps/sessions/services.py  (or apps/sessions/progress.py)
apps/sessions/tests/test_progress.py
```

---

### Task 3.4: Azure Speech-to-Text Integration Service

**Description**
Create a service wrapper around Azure Speech Services STT. Accepts audio input (base64 or binary), returns transcription text with confidence score. Handles timeouts, retries, and errors gracefully.

**Dependencies**
Task 1.7 (Azure Speech key)

**Inputs / Outputs**

- Input: Audio data (WAV/WebM), expected phoneme/word
- Output: `{ "text": "ship", "confidence": 0.85 }`

**Acceptance Criteria**

- Service calls Azure Speech SDK / REST API
- Returns structured result with text + confidence
- Timeout configurable (default 5s)
- Errors return a structured error response, never crash

**Test Strategy**

- Unit: Mock Azure SDK, verify service formats response correctly
- Unit: Timeout scenario returns error response
- Integration (manual): Send real audio, verify transcription

**Target Folder(s)**

```
apps/speech/services.py
apps/speech/azure_client.py
apps/speech/tests/test_services.py
```

---

### Task 3.5: Azure Text-to-Speech Integration Service

**Description**
Create a service wrapper for Azure TTS. Accepts text (phoneme sound or word), returns audio data (WAV/MP3) for playback. Uses child-friendly voice configuration.

**Dependencies**
Task 1.7 (Azure Speech key)

**Inputs / Outputs**

- Input: Text string (e.g., "sh", "ship")
- Output: Audio bytes (WAV/MP3)

**Acceptance Criteria**

- Service generates audio from text
- Voice configured for child-friendly tone
- Audio format suitable for browser playback
- Errors handled gracefully

**Test Strategy**

- Unit: Mock Azure SDK, verify correct parameters passed
- Unit: Response wraps audio bytes correctly
- Integration (manual): Generate audio, play in browser

**Target Folder(s)**

```
apps/speech/services.py  (or apps/speech/tts_service.py)
apps/speech/tests/test_tts.py
```

---

### Task 3.6: Speech Error Detection Logic

**Description**
Implement logic to detect common phoneme substitution errors by comparing expected phoneme against actual transcription. Returns error type (e.g., user said `/s/` instead of `/sh/`).

**Dependencies**
Task 3.4

**Inputs / Outputs**

- Input: Expected phoneme symbol, STT result text, confidence
- Output: `{ "is_correct": bool, "confidence": float, "detected_error": str|null }`

**Acceptance Criteria**

- Correctly identifies matching phoneme/word
- Detects common substitution (e.g., `/s/` for `/sh/`)
- Confidence below threshold (configurable) marked as low-confidence

**Test Strategy**

- Unit: Exact match → `is_correct=True`
- Unit: Common substitution → `detected_error="/s/"`
- Unit: Low confidence → flagged even if text matches

**Target Folder(s)**

```
apps/speech/error_detection.py
apps/speech/tests/test_error_detection.py
```

---

### Task 3.7: AI Tutor – Prompt Rendering Service

**Description**
Create a service that loads the active `PromptTemplate`, renders the system prompt and user context using provided variables (`phoneme`, `confidence`, `error`, `attempts`), and returns the formatted messages ready for LLM submission.

**Dependencies**
Task 2.6, Task 2.7

**Inputs / Outputs**

- Input: Phoneme context data (phoneme, confidence, error, attempts)
- Output: List of formatted messages `[{"role": "system", ...}, {"role": "user", ...}]`

**Acceptance Criteria**

- Active template loaded from database
- Variables correctly interpolated
- Missing variables raise clear error
- Output matches expected LLM message format

**Test Strategy**

- Unit: Render with sample data, verify output format
- Unit: Missing variable raises `ValueError`
- Unit: Inactive template not loaded

**Target Folder(s)**

```
apps/ai_tutor/services.py
apps/ai_tutor/tests/test_prompt_rendering.py
```

---

### Task 3.8: AI Tutor – Azure OpenAI Integration Service

**Description**
Create a service that sends rendered prompt messages to Azure OpenAI (via AI Foundry) and returns the LLM response text. Configure max tokens, temperature, and safety parameters.

**Dependencies**
Task 1.7 (Azure OpenAI key), Task 3.7

**Inputs / Outputs**

- Input: Formatted prompt messages
- Output: LLM response string

**Acceptance Criteria**

- Service calls Azure OpenAI API with correct endpoint/key
- Max tokens capped (e.g., 100) to enforce short responses
- Temperature set low (e.g., 0.3) for consistency
- Timeout and error handling in place

**Test Strategy**

- Unit: Mock Azure OpenAI client, verify parameters
- Unit: Timeout returns structured error
- Integration (manual): Send prompt, verify response is child-appropriate

**Target Folder(s)**

```
apps/ai_tutor/llm_client.py
apps/ai_tutor/tests/test_llm_client.py
```

---

### Task 3.9: AI Tutor – Response Validation & Safety Filter

**Description**
Implement a validator that checks LLM responses against safety rules: max length (1-2 sentences), no personal questions, no "wrong" keyword, no inappropriate content. Reject or sanitize non-compliant responses and return a safe fallback.

**Dependencies**
Task 3.8

**Inputs / Outputs**

- Input: Raw LLM response string
- Output: Validated response string (or safe fallback)

**Acceptance Criteria**

- Responses > 2 sentences truncated or replaced with fallback
- "wrong" keyword detected and replaced
- Personal questions detected and rejected
- Fallback message is always safe and encouraging

**Test Strategy**

- Unit: Clean response passes through unchanged
- Unit: Response with "wrong" → replaced with fallback
- Unit: Response with question mark + personal words → rejected
- Unit: Excessively long response → truncated

**Target Folder(s)**

```
apps/ai_tutor/validators.py
apps/ai_tutor/tests/test_validators.py
```

---

### Task 3.10: Feedback Strategy Engine

**Description**
Implement logic that selects a feedback strategy based on attempt count and confidence history: first attempt → simple encouragement, 2nd attempt → gentle guidance, 3+ attempts → adjusted approach (slower, simpler). Returns strategy metadata passed to prompt rendering.

**Dependencies**
Task 3.3, Task 3.7

**Inputs / Outputs**

- Input: Session ID, phoneme, current attempt data
- Output: `{ "strategy": "encourage|guide|adjust", "hints": [...] }`

**Acceptance Criteria**

- First attempt with good confidence → "encourage"
- Second attempt with low confidence → "guide"
- 3+ attempts → "adjust" with simplified hints
- Never returns discouraging content

**Test Strategy**

- Unit: 1 attempt, high confidence → "encourage"
- Unit: 2 attempts, low confidence → "guide"
- Unit: 4 attempts → "adjust" with hints
- Unit: Strategy metadata is valid for prompt rendering

**Target Folder(s)**

```
apps/ai_tutor/feedback.py
apps/ai_tutor/tests/test_feedback.py
```

---

### Task 3.11: Phonics REST API – List & Detail Endpoints

**Description**
Create DRF (Django REST Framework) viewset/views: `GET /api/phonics/categories/` (list categories), `GET /api/phonics/phonemes/?category=digraph` (list phonemes, filterable), `GET /api/phonics/phonemes/{symbol}/` (detail).

**Dependencies**
Task 3.1

**Inputs / Outputs**

- Input: HTTP GET requests
- Output: JSON responses with phoneme data

**Acceptance Criteria**

- Categories endpoint returns all 6 categories
- Phonemes filterable by category
- Detail endpoint returns full phoneme with example words
- Proper 404 for unknown phoneme

**Test Strategy**

- Unit: `APIClient.get("/api/phonics/categories/")` → 200, 6 items
- Unit: `APIClient.get("/api/phonics/phonemes/?category=digraph")` → correct subset
- Unit: `APIClient.get("/api/phonics/phonemes/zz/")` → 404

**Target Folder(s)**

```
apps/phonics/serializers.py
apps/phonics/views.py
apps/phonics/urls.py
apps/phonics/tests/test_api.py
```

---

### Task 3.12: Session REST API – Create & Retrieve Endpoints

**Description**
Create API endpoints: `POST /api/sessions/` (create new anonymous session), `GET /api/sessions/{session_id}/` (retrieve session with progress), `PATCH /api/sessions/{session_id}/` (update current phoneme).

**Dependencies**
Task 3.2

**Inputs / Outputs**

- Input: HTTP requests
- Output: JSON session data with UUID

**Acceptance Criteria**

- POST creates session, returns UUID
- GET returns session with current phoneme and progress summary
- PATCH updates current phoneme
- No PII in request or response

**Test Strategy**

- Unit: POST → 201, UUID in response
- Unit: GET with valid UUID → 200
- Unit: GET with invalid UUID → 404
- Unit: PATCH updates current_phoneme

**Target Folder(s)**

```
apps/sessions/serializers.py
apps/sessions/views.py
apps/sessions/urls.py
apps/sessions/tests/test_api.py
```

---

### Task 3.13: Speech REST API – Submit Attempt Endpoint

**Description**
Create `POST /api/speech/attempt/` endpoint that accepts audio data + session ID + expected phoneme, orchestrates STT → error detection → attempt recording → feedback generation, returns feedback response.

**Dependencies**
Task 3.4, Task 3.6, Task 3.3, Task 3.10, Task 3.7, Task 3.8, Task 3.9

**Inputs / Outputs**

- Input: `{ "session_id": "uuid", "phoneme": "sh", "audio": "<base64>" }`
- Output: `{ "confidence": 0.85, "is_correct": true, "feedback": "Great job! ...", "detected_error": null }`

**Acceptance Criteria**

- End-to-end: audio → STT → error detection → progress → AI feedback
- Response time < 1.5 seconds (measured, logged)
- Feedback follows safety rules
- Attempt recorded in database

**Test Strategy**

- Unit: Mock all external services, verify orchestration flow
- Unit: Low confidence triggers correct feedback strategy
- Integration: End-to-end with mocked Azure services

**Target Folder(s)**

```
apps/speech/views.py
apps/speech/serializers.py
apps/speech/urls.py
apps/speech/tests/test_api.py
```

---

### Task 3.14: Text-to-Speech REST API Endpoint

**Description**
Create `GET /api/speech/tts/?text=ship` endpoint that returns audio data for browser playback (audio/wav or audio/mpeg content type).

**Dependencies**
Task 3.5

**Inputs / Outputs**

- Input: `text` query parameter
- Output: Audio binary response with appropriate content type

**Acceptance Criteria**

- Returns audio content with correct MIME type
- Empty/missing text returns 400
- Audio playable in browser `<audio>` element

**Test Strategy**

- Unit: Mock TTS service, verify response headers
- Unit: Missing text → 400
- Integration (manual): Hit endpoint, play audio in browser

**Target Folder(s)**

```
apps/speech/views.py
apps/speech/urls.py
apps/speech/tests/test_api.py
```

---

### Task 3.15: Game REST API Endpoints

**Description**
Create: `GET /api/games/` (list active games), `GET /api/games/{id}/` (game detail with mapped phonemes), `GET /api/games/for-phoneme/{symbol}/` (games available for a specific phoneme).

**Dependencies**
Task 2.5, Task 3.1

**Inputs / Outputs**

- Input: HTTP GET requests
- Output: JSON game data with phoneme mappings

**Acceptance Criteria**

- Only active games returned in list
- Detail includes mapped phoneme symbols
- for-phoneme returns games relevant to that phoneme

**Test Strategy**

- Unit: List endpoint filters inactive games
- Unit: Detail includes phoneme list
- Unit: for-phoneme returns correct subset

**Target Folder(s)**

```
apps/games/serializers.py
apps/games/views.py
apps/games/urls.py
apps/games/tests/test_api.py
```

---

## Phase 4 – UI Components & Frontend Integration

---

### Task 4.1: Responsive Layout Shell & CSS Framework

**Description**
Implement the main app layout shell: header (with mascot placeholder), main content area, and navigation. CSS breakpoints: mobile (<768px), tablet (768–1023px), desktop (≥1024px). Large tap targets (min 48×48px). Touch-first design.

**Dependencies**
Task 1.9

**Inputs / Outputs**

- Input: `base.html`
- Output: Responsive shell with CSS grid/flexbox layout

**Acceptance Criteria**

- Layout adapts cleanly at 3 breakpoints
- No horizontal scroll at any width
- Tap targets ≥ 48px
- WCAG-aware color contrast (4.5:1 minimum)

**Test Strategy**

- Manual: Resize browser through all breakpoints
- Manual: Chrome DevTools device emulation (iPhone SE, iPad, Desktop)
- Manual: Contrast checker on primary colors

**Target Folder(s)**

```
static/css/layout.css
templates/base.html
templates/components/header.html
```

**Responsive Requirements**

- Mobile: Single-column, full-width buttons, bottom nav
- Tablet: Two-column where appropriate, side nav
- Desktop: Centered content, max-width 1200px

---

### Task 4.2: Mascot Component

**Description**
Create a reusable mascot UI component (SVG or image) that appears consistently across pages. Mascot has idle, happy, and encouraging states (CSS class-driven). Positioned in header on desktop, floating on mobile.

**Dependencies**
Task 4.1

**Inputs / Outputs**

- Input: Mascot image assets
- Output: `{% include "components/mascot.html" %}` with state support

**Acceptance Criteria**

- Mascot visible on all pages
- State changes via CSS class (`.mascot--idle`, `.mascot--happy`, `.mascot--encouraging`)
- Responsive positioning (header on desktop, fixed-bottom on mobile)

**Test Strategy**

- Manual: Verify mascot visible at all breakpoints
- Manual: Toggle CSS classes, verify visual state change
- Manual: Mascot does not obstruct content

**Target Folder(s)**

```
templates/components/mascot.html
static/css/mascot.css
static/images/mascot/
```

---

### Task 4.3: Phonics Category Selection Page

**Description**
Build a page displaying all phonics categories as large, tappable cards with icons/labels (≤5 words per label). Fetches categories from `GET /api/phonics/categories/`. Touch-first, audio cue on tap.

**Dependencies**
Task 3.11, Task 4.1

**Inputs / Outputs**

- Input: Categories API
- Output: Rendered page with category cards

**Acceptance Criteria**

- All 6 categories displayed
- Cards are large, tappable (≥ 48px touch target)
- No text > 5 words on any card
- Audio cue on category selection

**Test Strategy**

- Manual: All categories visible, tappable on mobile/tablet/desktop
- Unit: Django template renders correctly with mock context
- Manual: Verify audio plays on tap

**Target Folder(s)**

```
templates/phonics/categories.html
static/css/phonics.css
static/js/phonics.js
apps/phonics/views.py (template view)
```

**Responsive Requirements**

- Mobile: 1-column grid, full-width cards
- Tablet: 2-column grid
- Desktop: 3-column grid

---

### Task 4.4: Phoneme List Page (Per Category)

**Description**
Build a page listing phonemes within a selected category as tappable tiles. Each tile shows the phoneme symbol and one example word. Fetches from `GET /api/phonics/phonemes/?category=X`.

**Dependencies**
Task 3.11, Task 4.3

**Inputs / Outputs**

- Input: Category slug/name, Phonemes API
- Output: Phoneme tile grid

**Acceptance Criteria**

- Phonemes displayed in `display_order`
- Each tile ≤ 5 words
- Back navigation to categories
- Touch target ≥ 48px

**Test Strategy**

- Manual: Navigate from category → phoneme list, verify correct items
- Unit: Template renders correct phonemes for category
- Manual: Test at all 3 breakpoints

**Target Folder(s)**

```
templates/phonics/phoneme_list.html
apps/phonics/views.py
```

**Responsive Requirements**

- Mobile: 2-column grid
- Tablet: 3-column grid
- Desktop: 4-column grid

---

### Task 4.5: Learning Loop – Listen Step

**Description**
Build the "Listen" step of the learning loop. When a phoneme is selected, the TTS API is called and audio plays automatically. Shows the phoneme symbol prominently. User taps "Next" to proceed.

**Dependencies**
Task 3.14, Task 4.4

**Inputs / Outputs**

- Input: Selected phoneme, TTS endpoint
- Output: Audio playback + visual display of phoneme

**Acceptance Criteria**

- Audio plays automatically on page load (or on first tap for mobile autoplay policy)
- Phoneme symbol shown large and centered
- "Listen Again" button available
- "Next" button proceeds to Observe step
- Loop step < 3 minutes design target

**Test Strategy**

- Manual: Select phoneme → audio plays
- Manual: "Listen Again" replays audio
- Manual: Works on mobile (tap-to-start audio)

**Target Folder(s)**

```
templates/learning/listen.html
static/js/learning.js
static/css/learning.css
```

**Responsive Requirements**

- All breakpoints: Centered, large phoneme display, large buttons

---

### Task 4.6: Learning Loop – Observe Step

**Description**
Build the "Observe" step. Display the letter(s) with a simple CSS animation (e.g., scale-in, highlight). Show an example word with the phoneme highlighted within it. "Next" button proceeds to Repeat step.

**Dependencies**
Task 4.5

**Inputs / Outputs**

- Input: Phoneme data (symbol, example_words)
- Output: Animated letter display + highlighted example word

**Acceptance Criteria**

- Letter(s) animate in on page load
- Example word shows phoneme highlighted (e.g., **sh**ip)
- Animation is subtle, not distracting
- "Next" proceeds to Repeat

**Test Strategy**

- Manual: Verify animation plays
- Manual: Phoneme highlighted in example word
- Manual: Works at all breakpoints

**Target Folder(s)**

```
templates/learning/observe.html
static/css/animations.css
```

---

### Task 4.7: Learning Loop – Repeat Step (Speech Input)

**Description**
Build the "Repeat" step. Display a microphone button. On tap, capture audio via browser MediaRecorder API. Send audio to `POST /api/speech/attempt/`. Display feedback from AI tutor. Show retry or "Next" based on result.

**Dependencies**
Task 3.13, Task 4.6

**Inputs / Outputs**

- Input: User microphone audio, session ID, expected phoneme
- Output: AI feedback message, confidence indicator

**Acceptance Criteria**

- Microphone permission requested on first use
- Recording starts/stops with clear visual indicator
- Audio sent to speech API
- Feedback displayed with mascot state change (happy or encouraging)
- Response < 1.5 seconds (target)
- Retry available on low confidence

**Test Strategy**

- Manual: Tap mic → record → submit → see feedback
- Manual: Deny mic permission → graceful error message
- Manual: Test on mobile browser (Chrome, Safari)

**Target Folder(s)**

```
templates/learning/repeat.html
static/js/speech.js
static/css/learning.css
```

**Responsive Requirements**

- All breakpoints: Large centered microphone button (≥ 64px), feedback text below

---

### Task 4.8: Learning Loop – Practice Step (Game Launcher)

**Description**
Build the "Practice" step. Shows available games for the current phoneme (from `GET /api/games/for-phoneme/{symbol}/`). User selects a game to play. Each game is one learning objective.

**Dependencies**
Task 3.15, Task 4.7

**Inputs / Outputs**

- Input: Current phoneme, Games API
- Output: Game selection UI

**Acceptance Criteria**

- Available games for phoneme displayed as cards
- One game = one learning objective
- Selecting a game launches it (separate task for each game)
- "Skip" option proceeds to reinforce step

**Test Strategy**

- Manual: Games displayed for phoneme with games mapped
- Manual: Phoneme with no games → skip to reinforce
- Manual: Responsive at all breakpoints

**Target Folder(s)**

```
templates/learning/practice.html
static/js/games.js
```

---

### Task 4.9: Learning Loop – Reinforce Step

**Description**
Build the "Reinforce" step. Display encouraging message, reward animation (stars, confetti, or similar), and mascot in happy state. Show progress indicator. "Continue" button returns to phoneme list or advances to next phoneme.

**Dependencies**
Task 4.8, Task 3.3

**Inputs / Outputs**

- Input: Completion status, progress data
- Output: Celebration UI, progress indicator, navigation

**Acceptance Criteria**

- Encouraging message displayed (never "you got it wrong")
- Reward animation plays
- Mascot switches to happy state
- Progress bar/indicator updated
- "Continue" → next phoneme or category list

**Test Strategy**

- Manual: Complete a phoneme → reinforce shows celebration
- Manual: Progress bar advances
- Manual: Visual works at all breakpoints

**Target Folder(s)**

```
templates/learning/reinforce.html
static/css/animations.css
static/js/rewards.js
```

---

### Task 4.10: Game – Sound → Picture Matching

**Description**
Build the Sound-Picture matching game. Audio plays a phoneme sound, child selects the correct picture from 3-4 options. Correct → celebration, incorrect → gentle retry.

**Dependencies**
Task 3.14, Task 3.15, Task 4.1

**Inputs / Outputs**

- Input: Phoneme, TTS audio, image options
- Output: Interactive game with audio + tappable images

**Acceptance Criteria**

- Audio plays phoneme sound
- 3–4 picture options displayed as large tappable cards
- Correct selection → celebration animation + mascot happy
- Incorrect → gentle encouragement, try again
- Never says "wrong"

**Test Strategy**

- Manual: Play game → select correct picture → celebration
- Manual: Select incorrect → encouragement, not "wrong"
- Manual: Touch-friendly on mobile

**Target Folder(s)**

```
templates/games/sound_picture.html
static/js/games/sound_picture.js
static/css/games.css
static/images/game_assets/
```

**Responsive Requirements**

- Mobile: 2×2 picture grid
- Tablet/Desktop: 1×4 horizontal row

---

### Task 4.11: Game – Beginning Sound Selection

**Description**
Build the Beginning Sound game. Display a word/picture, child selects the correct beginning sound from 3-4 letter options.

**Dependencies**
Task 3.15, Task 4.1

**Inputs / Outputs**

- Input: Target word, letter options (1 correct + 2-3 distractors)
- Output: Interactive selection game

**Acceptance Criteria**

- Word/picture displayed prominently
- 3-4 letter options as large buttons
- Correct → celebration
- Incorrect → gentle redo

**Test Strategy**

- Manual: Play game, select correct beginning sound
- Manual: Incorrect selection → encouragement
- Manual: Responsive at all breakpoints

**Target Folder(s)**

```
templates/games/beginning_sound.html
static/js/games/beginning_sound.js
```

---

### Task 4.12: Game – Blend Builder (Drag & Drop)

**Description**
Build the Blend Builder game. Display scattered letter tiles. Child drags letters into the correct order to form a word. Uses HTML5 Drag and Drop API (with touch polyfill for mobile).

**Dependencies**
Task 3.15, Task 4.1

**Inputs / Outputs**

- Input: Target word, individual letters
- Output: Drag-and-drop interface

**Acceptance Criteria**

- Letter tiles draggable on desktop (mouse) and mobile (touch)
- Drop zone shows forming word
- Correct order → celebration
- Wrong placement → tile bounces back
- Accessible: keyboard alternative available

**Test Strategy**

- Manual: Drag letters into correct order → win
- Manual: Test touch drag on mobile device
- Manual: Keyboard tab + enter as alternative

**Target Folder(s)**

```
templates/games/blend_builder.html
static/js/games/blend_builder.js
static/js/lib/touch-dnd-polyfill.js (if needed)
```

**Responsive Requirements**

- Mobile: Vertical layout, tiles above drop zone
- Desktop: Horizontal layout

---

### Task 4.13: Game – Balloon Pop

**Description**
Build the Balloon Pop game. Balloons float up with letters/phonemes on them. Child taps/clicks balloons with the correct sound. Correct balloon pops, incorrect does not.

**Dependencies**
Task 3.15, Task 4.1

**Inputs / Outputs**

- Input: Target phoneme, distractor phonemes
- Output: Animated balloon game

**Acceptance Criteria**

- Balloons animate upward continuously
- Tapping correct balloon → pop animation + sound + point
- Tapping incorrect → balloon wobbles, no pop
- Game ends after set number of correct pops (e.g., 5)
- Touch and mouse input supported

**Test Strategy**

- Manual: Pop correct balloons → score increases
- Manual: Incorrect balloon → no pop
- Manual: Game ends correctly
- Manual: Works on mobile touch

**Target Folder(s)**

```
templates/games/balloon_pop.html
static/js/games/balloon_pop.js
static/css/games/balloon_pop.css
```

**Responsive Requirements**

- All breakpoints: Full-width game area, balloon size scales with viewport

---

## Phase 5 – Observability & Demo Diagnostics

---

### Task 5.1: Attempt Logging Middleware

**Description**
Implement Django middleware or signal-based logging that records: phoneme attempted, confidence, error type, AI feedback type, timestamp. Logs to Django logger (structured JSON format).

**Dependencies**
Task 3.13

**Inputs / Outputs**

- Input: Speech attempt requests
- Output: Structured log entries

**Acceptance Criteria**

- Every speech attempt generates a log entry
- Log includes: phoneme, confidence, error, feedback_strategy, response_time_ms
- Structured JSON format for log parsing

**Test Strategy**

- Unit: Mock request → verify log entry generated
- Unit: Log entry contains all required fields
- Integration: Submit attempt → check log output

**Target Folder(s)**

```
apps/speech/middleware.py (or apps/speech/signals.py)
config/settings/base.py (LOGGING config)
```

---

### Task 5.2: Diagnostics Dashboard – Data Aggregation API

**Description**
Create API endpoints for dashboard data: `GET /api/diagnostics/phoneme-success/` (success rate per phoneme), `GET /api/diagnostics/time-spent/` (avg time per phoneme), `GET /api/diagnostics/retry-rates/` (avg retries per phoneme).

**Dependencies**
Task 2.4, Task 3.3

**Inputs / Outputs**

- Input: SpeechAttempt data
- Output: Aggregated statistics JSON

**Acceptance Criteria**

- Success rate = attempts with confidence ≥ threshold / total attempts
- Time spent = avg duration between first and last attempt per phoneme per session
- Retry rate = avg attempt_number per phoneme
- Data filterable by date range

**Test Strategy**

- Unit: Seed 20 attempts, verify aggregation math
- Unit: Empty data returns zeros, not errors
- Unit: Date range filter works

**Target Folder(s)**

```
apps/sessions/diagnostics.py
apps/sessions/views.py
apps/sessions/tests/test_diagnostics.py
```

---

### Task 5.3: Diagnostics Dashboard – UI

**Description**
Build a simple, read-only dashboard page (for parents/teachers/stakeholders) showing: phoneme success chart, time-spent chart, retry rate chart. Uses simple chart library (e.g., Chart.js) or plain HTML tables.

**Dependencies**
Task 5.2, Task 4.1

**Inputs / Outputs**

- Input: Diagnostics API data
- Output: Visual dashboard page

**Acceptance Criteria**

- 3 charts/tables: success rate, time spent, retry rates
- Data loads from API endpoints
- Responsive layout
- Read-only, no editing capability

**Test Strategy**

- Manual: Dashboard renders with sample data
- Manual: Charts display correctly at all breakpoints
- Manual: Loading states shown while fetching data

**Target Folder(s)**

```
templates/diagnostics/dashboard.html
static/js/diagnostics.js
static/css/diagnostics.css
```

**Responsive Requirements**

- Mobile: Stacked charts, full-width
- Tablet/Desktop: Grid of charts

---

## Phase 6 – Safety, Compliance & Hardening

---

### Task 6.1: Input Sanitization & Safety Middleware

**Description**
Implement middleware/validation ensuring: no free-text input accepted from child-facing endpoints, no PII fields in any request, audio-only input on speech endpoints.

**Dependencies**
Task 3.13

**Inputs / Outputs**

- Input: All incoming requests
- Output: Rejected requests with text fields on child endpoints

**Acceptance Criteria**

- Child-facing endpoints reject unexpected text fields
- No endpoint accepts name, email, or other PII fields
- Audio submissions validated for format/size limits

**Test Strategy**

- Unit: POST with extra text fields → 400
- Unit: POST with PII-like fields → 400
- Unit: Oversized audio → 400 with clear message

**Target Folder(s)**

```
apps/speech/validators.py
config/middleware.py
apps/speech/tests/test_safety.py
```

---

### Task 6.2: AI Response Safety Integration Test Suite

**Description**
Create a comprehensive test suite that sends various prompt contexts to the AI pipeline (mocked LLM) and validates all responses meet child safety rules: no "wrong", no personal questions, short sentences, encouraging tone.

**Dependencies**
Task 3.9

**Inputs / Outputs**

- Input: Diverse prompt scenarios (high confidence, low confidence, repeated failure, edge cases)
- Output: All responses pass safety validation

**Acceptance Criteria**

- ≥ 20 test scenarios covering normal and edge cases
- All scenarios produce safe feedback
- Fallback used when LLM response fails validation
- No test allows "wrong" in output

**Test Strategy**

- Unit: 20+ parameterized tests with mocked LLM responses
- Unit: Deliberately unsafe LLM responses → fallback triggered

**Target Folder(s)**

```
apps/ai_tutor/tests/test_safety_integration.py
```

---

### Task 6.3: Session Data Auto-Purge Configuration

**Description**
Configure the session purge command (Task 2.8) to run automatically via Django management command scheduled with a simple cron-like mechanism or Celery beat (or Azure equivalent). Default: purge every 6 hours for data > 24 hours.

**Dependencies**
Task 2.8

**Inputs / Outputs**

- Input: Cron schedule configuration
- Output: Automatic session cleanup

**Acceptance Criteria**

- Purge runs on schedule
- Retention period configurable via environment variable
- Purge logged (count of deleted sessions)

**Test Strategy**

- Integration: Run management command, verify deletion
- Manual: Verify scheduled execution in deployment environment

**Target Folder(s)**

```
apps/sessions/management/commands/purge_expired_sessions.py
config/settings/base.py (schedule config)
```

---

## Phase 7 – Deployment & Azure Configuration

---

### Task 7.0: Infrastructure as Code (Bicep)

**Description**
Define all Azure infrastructure in declarative Bicep templates, replacing ad-hoc CLI provisioning. A single `az deployment group create` command provisions every resource (App Service Plan, Web App, PostgreSQL Flexible Server, Speech Services, Azure OpenAI + model deployment, Log Analytics) and wires secrets into App Settings automatically.

**Dependencies**
All previous phases (infrastructure is deployed last)

**Inputs / Outputs**

- Input: Bicep templates + parameter file
- Output: Fully provisioned Azure environment with all resources connected

**Acceptance Criteria**

- `az bicep build` compiles without errors
- Single deployment command provisions all resources
- Re-running the deployment is idempotent
- Secrets flow from Bicep params/outputs into App Settings (never hard-coded)
- A second environment can be stood up with a different parameter file
- `az deployment group what-if` previews changes correctly

**Test Strategy**

- Validation: `az bicep build --file infra/main.bicep` passes
- Integration: Deploy to test resource group → verify all resources in Portal
- Integration: Re-deploy → verify idempotent (no changes)
- Manual: `az group delete` tears down cleanly

**Target Folder(s)**

```
PhonicsApp/
└── infra/
    ├── main.bicep
    ├── main.bicepparam
    ├── modules/
    │   ├── app-service.bicep
    │   ├── database.bicep
    │   ├── speech.bicep
    │   ├── openai.bicep
    │   └── monitoring.bicep
    └── README.md
```

---

### Task 7.1: Azure App Service Deployment Configuration

**Description**
Create deployment configuration for Azure App Service: `Dockerfile` or App Service configuration, `startup.sh`, production settings with `ALLOWED_HOSTS`, `STATIC_ROOT`, database SSL, and gunicorn/uvicorn.

**Dependencies**
All previous phases (deployment is last)

**Inputs / Outputs**

- Input: Django project
- Output: Deployable configuration for Azure App Service

**Acceptance Criteria**

- App deploys and starts on Azure App Service
- Static files served correctly
- Database connects via SSL
- Environment variables read from Azure App Settings

**Test Strategy**

- Integration: Deploy to staging, verify homepage loads
- Integration: Verify API endpoints return data
- Manual: Static files (CSS/JS) load correctly

**Target Folder(s)**

```
PhonicsApp/
├── Dockerfile (or .deployment)
├── startup.sh
└── config/settings/prod.py
```

---

### Task 7.2: Azure Speech Services Provisioning & Config

**Description**
Document and configure Azure Speech Services: resource creation, key/endpoint environment variables, region configuration. Verify STT and TTS work against Azure.

**Dependencies**
Task 3.4, Task 3.5

**Inputs / Outputs**

- Input: Azure subscription
- Output: Working Speech Services integration

**Acceptance Criteria**

- STT endpoint responds with transcription
- TTS endpoint returns audio
- Keys stored as environment variables (not in code)

**Test Strategy**

- Integration: Send test audio → receive transcription
- Integration: Send test text → receive audio
- Manual: Verify in Azure portal

**Target Folder(s)**

```
docs/deployment/azure_speech_setup.md
config/settings/prod.py
```

---

### Task 7.3: Azure OpenAI Provisioning & Config

**Description**
Document and configure Azure OpenAI (via AI Foundry): model deployment, endpoint/key configuration, content safety filters enabled.

**Dependencies**
Task 3.8

**Inputs / Outputs**

- Input: Azure subscription
- Output: Working Azure OpenAI integration

**Acceptance Criteria**

- LLM responds to prompt templates
- Content safety filter enabled at Azure level
- Keys/endpoints as environment variables

**Test Strategy**

- Integration: Send sample prompt → receive child-safe response
- Manual: Verify content safety settings in Azure portal

**Target Folder(s)**

```
docs/deployment/azure_openai_setup.md
config/settings/prod.py
```

---

## Phase 8 – Authentication & Access Control

---

### Task 8.1: Azure Easy Auth with Microsoft Entra ID

**Description**
Enable Azure App Service built-in authentication ("Easy Auth") with Microsoft Entra ID as the identity provider. Configure selective route protection so the main learning app remains anonymous for children, while the diagnostics dashboard and Django admin require login. Add lightweight Django middleware to read Easy Auth headers (`X-MS-CLIENT-PRINCIPAL-NAME`, `X-MS-CLIENT-PRINCIPAL-ID`) and map them to Django's `request.user` for protected views.

**Dependencies**
Task 7.1, Task 5.3

**Inputs / Outputs**

- Input: Deployed App Service from Task 7.1; diagnostics dashboard from Task 5.3
- Output: Entra ID app registration; Easy Auth enabled; protected routes require login; anonymous child sessions unaffected

**Acceptance Criteria**

- Entra ID app registration created with correct redirect URIs
- Easy Auth enabled on the App Service with "Allow unauthenticated access" (so children can use the main app)
- `/diagnostics/` and `/admin/` routes require authentication (enforced via Django middleware reading Easy Auth headers)
- Unauthenticated requests to protected routes redirect to Microsoft login
- Authenticated user identity available in Django via `request.user`
- Main learning flows (`/`, `/phonics/`, `/games/`, `/api/`) remain fully anonymous
- Local development works without Easy Auth (middleware gracefully skips when headers are absent)

**Test Strategy**

- Integration: Access `/diagnostics/` without auth → redirected to login
- Integration: Access `/phonics/` without auth → page loads normally
- Unit: Middleware sets `request.user` when Easy Auth headers present
- Unit: Middleware allows anonymous access when headers absent
- Manual: Deploy → sign in via Microsoft → verify diagnostics dashboard accessible
- Manual: Open main app in incognito → verify child learning flow works without login

**Target Folder(s)**

```
docs/deployment/azure_auth_setup.md        # Entra ID + Easy Auth provisioning guide
apps/common/middleware/easyauth.py          # Middleware to map Easy Auth headers to Django user
config/settings/base.py                     # Middleware registration
config/settings/prod.py                     # AUTH-related settings
```

---

## Dependency Graph Summary

```
Phase 1 (Foundations)
├── 1.1 Django Project
│   ├── 1.2–1.6 App Skeletons (parallel)
│   ├── 1.7 Env Config
│   │   └── 1.8 Database Config
│   ├── 1.9 Static/Templates
│   └── 1.10 Dev Tooling
│
Phase 2 (Models)
├── 2.1 Phoneme Model ← 1.2, 1.8
│   ├── 2.2 Seed Data
│   ├── 2.3 Session Model
│   │   ├── 2.4 SpeechAttempt Model
│   │   └── 2.8 Session Expiry
│   └── 2.5 Game Models
├── 2.6 PromptTemplate Model ← 1.5
│   └── 2.7 Seed Prompts
│
Phase 3 (Services & APIs)
├── 3.1 Phonics Service ← 2.1, 2.2
├── 3.2 Session Service ← 2.3
├── 3.3 Progress Service ← 2.3, 2.4, 3.1
├── 3.4 STT Service ← 1.7
├── 3.5 TTS Service ← 1.7
├── 3.6 Error Detection ← 3.4
├── 3.7 Prompt Rendering ← 2.6, 2.7
├── 3.8 LLM Client ← 1.7, 3.7
├── 3.9 Safety Validator ← 3.8
├── 3.10 Feedback Strategy ← 3.3, 3.7
├── 3.11 Phonics API ← 3.1
├── 3.12 Session API ← 3.2
├── 3.13 Speech API ← 3.4, 3.6, 3.3, 3.10, 3.8, 3.9
├── 3.14 TTS API ← 3.5
├── 3.15 Games API ← 2.5, 3.1
│
Phase 4 (UI)
├── 4.1 Layout Shell ← 1.9
├── 4.2 Mascot ← 4.1
├── 4.3 Category Page ← 3.11, 4.1
├── 4.4 Phoneme List ← 3.11, 4.3
├── 4.5 Listen Step ← 3.14, 4.4
├── 4.6 Observe Step ← 4.5
├── 4.7 Repeat Step ← 3.13, 4.6
├── 4.8 Practice Step ← 3.15, 4.7
├── 4.9 Reinforce Step ← 4.8, 3.3
├── 4.10–4.13 Games ← 3.15, 4.1
│
Phase 5 (Observability)
├── 5.1 Logging ← 3.13
├── 5.2 Diagnostics API ← 2.4, 3.3
├── 5.3 Dashboard UI ← 5.2, 4.1
│
Phase 6 (Safety)
├── 6.1 Input Sanitization ← 3.13
├── 6.2 Safety Tests ← 3.9
├── 6.3 Auto-Purge ← 2.8
│
Phase 7 (Deployment)
├── 7.0 Infrastructure as Code (Bicep) ← all
├── 7.1 App Service Config ← 7.0
├── 7.2 Speech Services ← 7.0, 3.4, 3.5
├── 7.3 OpenAI Config ← 7.0, 3.8
│
Phase 8 (Authentication)
├── 8.1 Easy Auth + Entra ID ← 7.1, 5.3
```

---

**Total Tasks: 40**

- Phase 1 (Foundations): 10 tasks
- Phase 2 (Data Models): 8 tasks
- Phase 3 (Services & APIs): 15 tasks
- Phase 4 (UI): 13 tasks
- Phase 5 (Observability): 3 tasks
- Phase 6 (Safety): 3 tasks
- Phase 7 (Deployment): 4 tasks
- Phase 8 (Authentication): 1 task
