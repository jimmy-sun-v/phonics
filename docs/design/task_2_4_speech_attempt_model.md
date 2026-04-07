# Design: Task 2.4 – SpeechAttempt Model & Migration

## Overview

Define the `SpeechAttempt` model in the `speech` app to record each child's pronunciation attempt with confidence scores and error detection.

## Dependencies

- Task 2.1 (Phoneme model)
- Task 2.3 (LearningSession model)

## Detailed Design

### Model Definition

**File: `apps/speech/models.py`**

```python
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class SpeechAttempt(models.Model):
    session = models.ForeignKey(
        "learning_sessions.LearningSession",
        on_delete=models.CASCADE,
        related_name="speech_attempts",
        help_text="The learning session this attempt belongs to",
    )
    phoneme = models.ForeignKey(
        "phonics.Phoneme",
        on_delete=models.CASCADE,
        related_name="speech_attempts",
        help_text="The phoneme that was being practiced",
    )
    confidence = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Speech recognition confidence score (0.0–1.0)",
    )
    detected_error = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Detected substitution error, e.g., '/s/' for '/sh/'",
    )
    attempt_number = models.PositiveIntegerField(
        help_text="Sequential attempt number for this phoneme in this session",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this attempt was recorded",
    )

    class Meta:
        ordering = ["session", "phoneme", "attempt_number"]
        verbose_name = "Speech Attempt"
        verbose_name_plural = "Speech Attempts"
        indexes = [
            models.Index(fields=["session", "phoneme"], name="idx_attempt_session_phoneme"),
        ]

    def __str__(self):
        return f"Attempt {self.attempt_number}: {self.phoneme.symbol} (conf={self.confidence:.2f})"
```

### Field Details

| Field | Type | Notes |
|-------|------|-------|
| `session` | FK → LearningSession | CASCADE delete — when session is purged, attempts go too |
| `phoneme` | FK → Phoneme | CASCADE delete — if phoneme removed, attempts are invalidated |
| `confidence` | FloatField | Validated 0.0–1.0. Comes from Azure STT. |
| `detected_error` | CharField(50) | Nullable. E.g., "/s/" when child says "sip" instead of "ship" |
| `attempt_number` | PositiveIntegerField | Auto-incremented per (session, phoneme) by the service layer (Task 3.3) |
| `created_at` | DateTimeField | `auto_now_add=True` — immutable after creation |

### Composite Index

`idx_attempt_session_phoneme` on `(session, phoneme)` — optimizes the common query pattern:
```python
SpeechAttempt.objects.filter(session=session, phoneme=phoneme).count()
```

### Admin Registration

**File: `apps/speech/admin.py`**

```python
from django.contrib import admin
from .models import SpeechAttempt


@admin.register(SpeechAttempt)
class SpeechAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "phoneme", "confidence", "detected_error", "attempt_number", "created_at")
    list_filter = ("phoneme__category",)
    readonly_fields = ("created_at",)
    search_fields = ("session__session_id",)
```

### Migration

```powershell
python manage.py makemigrations speech
python manage.py migrate
```

## Acceptance Criteria

- [ ] SpeechAttempt linked to both session and phoneme via FKs
- [ ] Confidence validated 0.0–1.0 (rejects values outside range)
- [ ] `attempt_number` is a positive integer
- [ ] CASCADE delete: deleting session deletes its attempts
- [ ] CASCADE delete: deleting phoneme deletes its attempts

## Test Strategy

**File: `apps/speech/tests/test_models.py`**

```python
import pytest
from django.core.exceptions import ValidationError
from apps.speech.models import SpeechAttempt
from apps.sessions.models import LearningSession
from apps.phonics.models import Phoneme


@pytest.mark.django_db
class TestSpeechAttemptModel:
    @pytest.fixture
    def session(self):
        return LearningSession.objects.create()

    @pytest.fixture
    def phoneme(self):
        return Phoneme.objects.create(symbol="sh", category="digraph", example_words=["ship"])

    def test_create_attempt(self, session, phoneme):
        attempt = SpeechAttempt.objects.create(
            session=session, phoneme=phoneme, confidence=0.85, attempt_number=1
        )
        assert attempt.pk is not None
        assert attempt.confidence == 0.85

    def test_confidence_out_of_range_rejected(self, session, phoneme):
        attempt = SpeechAttempt(
            session=session, phoneme=phoneme, confidence=1.5, attempt_number=1
        )
        with pytest.raises(ValidationError):
            attempt.full_clean()

    def test_confidence_negative_rejected(self, session, phoneme):
        attempt = SpeechAttempt(
            session=session, phoneme=phoneme, confidence=-0.1, attempt_number=1
        )
        with pytest.raises(ValidationError):
            attempt.full_clean()

    def test_cascade_on_session_delete(self, session, phoneme):
        SpeechAttempt.objects.create(
            session=session, phoneme=phoneme, confidence=0.5, attempt_number=1
        )
        session.delete()
        assert SpeechAttempt.objects.count() == 0

    def test_cascade_on_phoneme_delete(self, session, phoneme):
        SpeechAttempt.objects.create(
            session=session, phoneme=phoneme, confidence=0.5, attempt_number=1
        )
        phoneme.delete()
        assert SpeechAttempt.objects.count() == 0

    def test_detected_error_nullable(self, session, phoneme):
        attempt = SpeechAttempt.objects.create(
            session=session, phoneme=phoneme, confidence=0.9, attempt_number=1, detected_error=None
        )
        assert attempt.detected_error is None
```
