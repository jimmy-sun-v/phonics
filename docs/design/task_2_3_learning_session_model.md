# Design: Task 2.3 – LearningSession Model & Migration

## Overview

Define the `LearningSession` model in the `sessions` app for tracking anonymous child learning sessions.

## Dependencies

- Task 2.1 (Phoneme model — FK target)

## Detailed Design

### Model Definition

**File: `apps/sessions/models.py`**

```python
import uuid
from django.db import models


class LearningSession(models.Model):
    session_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Auto-generated anonymous session identifier",
    )
    current_phoneme = models.ForeignKey(
        "phonics.Phoneme",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="active_sessions",
        help_text="The phoneme the child is currently working on",
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the session was created",
    )
    last_active_at = models.DateTimeField(
        auto_now=True,
        help_text="Last activity timestamp (auto-updated on save)",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this session is still active",
    )

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Learning Session"
        verbose_name_plural = "Learning Sessions"

    def __str__(self):
        return f"Session {self.session_id} ({'active' if self.is_active else 'inactive'})"
```

### Field Details

| Field | Type | Notes |
|-------|------|-------|
| `session_id` | UUIDField (PK) | Auto-generated via `uuid.uuid4`. No sequential IDs exposed. No PII. |
| `current_phoneme` | FK → Phoneme | `SET_NULL` on phoneme deletion. Nullable for new sessions. |
| `started_at` | DateTimeField | `auto_now_add=True` — set once at creation. |
| `last_active_at` | DateTimeField | `auto_now=True` — updated on every `.save()` call. |
| `is_active` | BooleanField | Indexed for filtering active sessions. |

### Admin Registration

**File: `apps/sessions/admin.py`**

```python
from django.contrib import admin
from .models import LearningSession


@admin.register(LearningSession)
class LearningSessionAdmin(admin.ModelAdmin):
    list_display = ("session_id", "current_phoneme", "started_at", "last_active_at", "is_active")
    list_filter = ("is_active", "started_at")
    readonly_fields = ("session_id", "started_at", "last_active_at")
    search_fields = ("session_id",)
```

### Migration

```powershell
python manage.py makemigrations learning_sessions
python manage.py migrate
```

Note: The migration command uses `learning_sessions` (the app label) not `sessions`.

### Database Schema

Table: `learning_sessions_learningsession`

| Column | Type | Constraints |
|--------|------|-------------|
| session_id | uuid | PK, default uuid4 |
| current_phoneme_id | bigint | FK → phonics_phoneme(id), NULL |
| started_at | timestamp with tz | NOT NULL, auto |
| last_active_at | timestamp with tz | NOT NULL, auto |
| is_active | boolean | NOT NULL, default true, indexed |

## Acceptance Criteria

- [ ] Session can be created with auto-generated UUID PK
- [ ] FK to Phoneme works correctly (including SET_NULL on delete)
- [ ] `last_active_at` updates on every `.save()`
- [ ] `started_at` does not change after initial creation
- [ ] Admin shows session details with read-only ID and timestamps

## Test Strategy

**File: `apps/sessions/tests/test_models.py`**

```python
import pytest
from uuid import UUID
from apps.sessions.models import LearningSession
from apps.phonics.models import Phoneme


@pytest.mark.django_db
class TestLearningSessionModel:
    def test_create_session_auto_uuid(self):
        session = LearningSession.objects.create()
        assert isinstance(session.session_id, UUID)

    def test_session_defaults(self):
        session = LearningSession.objects.create()
        assert session.is_active is True
        assert session.current_phoneme is None
        assert session.started_at is not None
        assert session.last_active_at is not None

    def test_assign_phoneme_fk(self):
        phoneme = Phoneme.objects.create(symbol="sh", category="digraph")
        session = LearningSession.objects.create(current_phoneme=phoneme)
        session.refresh_from_db()
        assert session.current_phoneme == phoneme

    def test_phoneme_delete_sets_null(self):
        phoneme = Phoneme.objects.create(symbol="ch", category="digraph")
        session = LearningSession.objects.create(current_phoneme=phoneme)
        phoneme.delete()
        session.refresh_from_db()
        assert session.current_phoneme is None

    def test_last_active_at_updates_on_save(self):
        session = LearningSession.objects.create()
        original = session.last_active_at
        session.is_active = False
        session.save()
        session.refresh_from_db()
        assert session.last_active_at >= original

    def test_str_representation(self):
        session = LearningSession.objects.create()
        assert "active" in str(session)
```
