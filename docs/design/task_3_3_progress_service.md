# Design: Task 3.3 – Progress Tracking Service

## Overview

Create a service to track learning progress per session: recording attempts, checking phoneme completion, and summarizing progress.

## Dependencies

- Task 2.3 (LearningSession model)
- Task 2.4 (SpeechAttempt model)
- Task 3.1 (Phonics service for phoneme data)

## Detailed Design

### Service Module

**File: `apps/sessions/progress.py`**

```python
from django.conf import settings
from django.db.models import Max
from apps.sessions.models import LearningSession
from apps.speech.models import SpeechAttempt
from apps.phonics.models import Phoneme


def get_confidence_threshold() -> float:
    return getattr(settings, "PHONEME_COMPLETION_THRESHOLD", 0.7)


def record_attempt(
    session_id,
    phoneme_symbol: str,
    confidence: float,
    error: str | None = None,
) -> SpeechAttempt:
    """Record a speech attempt for a session/phoneme.

    Automatically assigns the next attempt_number for the given
    session+phoneme combination.

    Args:
        session_id: UUID of the learning session.
        phoneme_symbol: The phoneme symbol being practiced.
        confidence: STT confidence score (0.0–1.0).
        error: Detected substitution error (optional).

    Returns:
        Created SpeechAttempt instance.
    """
    session = LearningSession.objects.get(session_id=session_id)
    phoneme = Phoneme.objects.get(symbol=phoneme_symbol)

    # Determine next attempt number
    max_attempt = (
        SpeechAttempt.objects
        .filter(session=session, phoneme=phoneme)
        .aggregate(max_num=Max("attempt_number"))
    )
    next_number = (max_attempt["max_num"] or 0) + 1

    attempt = SpeechAttempt.objects.create(
        session=session,
        phoneme=phoneme,
        confidence=confidence,
        detected_error=error,
        attempt_number=next_number,
    )

    # Touch the session to update last_active_at
    session.save()

    return attempt


def get_progress(session_id) -> dict:
    """Get learning progress summary for a session.

    Returns:
        {
            "completed": [{"symbol": "sh", "best_confidence": 0.92}, ...],
            "in_progress": [{"symbol": "th", "attempts": 2, "best_confidence": 0.55}, ...],
            "remaining": [{"symbol": "ch"}, ...],
            "total_phonemes": 59,
            "completed_count": 5,
            "completion_percentage": 8.5,
        }
    """
    session = LearningSession.objects.get(session_id=session_id)
    threshold = get_confidence_threshold()

    all_phonemes = Phoneme.objects.all()
    attempts = SpeechAttempt.objects.filter(session=session)

    # Group attempts by phoneme
    attempted_phonemes = {}
    for attempt in attempts.select_related("phoneme"):
        pid = attempt.phoneme_id
        if pid not in attempted_phonemes:
            attempted_phonemes[pid] = {
                "symbol": attempt.phoneme.symbol,
                "attempts": 0,
                "best_confidence": 0.0,
            }
        attempted_phonemes[pid]["attempts"] += 1
        attempted_phonemes[pid]["best_confidence"] = max(
            attempted_phonemes[pid]["best_confidence"],
            attempt.confidence,
        )

    completed = []
    in_progress = []
    remaining = []
    attempted_ids = set(attempted_phonemes.keys())

    for phoneme in all_phonemes:
        if phoneme.id in attempted_ids:
            data = attempted_phonemes[phoneme.id]
            if data["best_confidence"] >= threshold:
                completed.append({
                    "symbol": data["symbol"],
                    "best_confidence": data["best_confidence"],
                })
            else:
                in_progress.append(data)
        else:
            remaining.append({"symbol": phoneme.symbol})

    total = all_phonemes.count()
    completed_count = len(completed)

    return {
        "completed": completed,
        "in_progress": in_progress,
        "remaining": remaining,
        "total_phonemes": total,
        "completed_count": completed_count,
        "completion_percentage": round((completed_count / total) * 100, 1) if total > 0 else 0,
    }


def get_attempts_for_phoneme(session_id, phoneme_symbol: str) -> list[SpeechAttempt]:
    """Get all attempts for a specific phoneme in a session.

    Returns:
        List of SpeechAttempt objects ordered by attempt_number.
    """
    return list(
        SpeechAttempt.objects.filter(
            session_id=session_id,
            phoneme__symbol=phoneme_symbol,
        ).order_by("attempt_number")
    )
```

### Design Decisions

1. **Auto-incrementing `attempt_number`**: Calculated via `MAX(attempt_number) + 1` per (session, phoneme) pair. This is simpler than a DB sequence and tolerates concurrent requests via the aggregate.
2. **Completion threshold**: Phoneme is "completed" when any attempt achieves `confidence >= PHONEME_COMPLETION_THRESHOLD`.
3. **Progress categories**: Three states — completed, in_progress (attempted but not yet passing), remaining (never attempted).
4. **Percentage**: Rounded to 1 decimal place for UI display.

## Acceptance Criteria

- [ ] `record_attempt` auto-increments attempt_number (1, 2, 3...)
- [ ] `get_progress` returns correct completed/in_progress/remaining counts
- [ ] Phoneme with confidence ≥ 0.7 listed as completed
- [ ] Phoneme with confidence < 0.7 listed as in_progress
- [ ] Never-attempted phonemes listed as remaining

## Test Strategy

**File: `apps/sessions/tests/test_progress.py`**

```python
import pytest
from apps.sessions.progress import record_attempt, get_progress, get_attempts_for_phoneme
from apps.sessions.models import LearningSession
from apps.phonics.models import Phoneme


@pytest.mark.django_db
class TestProgressTracking:
    @pytest.fixture
    def session(self):
        return LearningSession.objects.create()

    @pytest.fixture
    def phoneme(self):
        return Phoneme.objects.create(symbol="sh", category="digraph", example_words=["ship"])

    def test_record_attempt_auto_increments(self, session, phoneme):
        a1 = record_attempt(session.session_id, "sh", 0.5)
        a2 = record_attempt(session.session_id, "sh", 0.7)
        a3 = record_attempt(session.session_id, "sh", 0.9)
        assert a1.attempt_number == 1
        assert a2.attempt_number == 2
        assert a3.attempt_number == 3

    def test_progress_completed(self, session, phoneme):
        record_attempt(session.session_id, "sh", 0.9)
        progress = get_progress(session.session_id)
        assert len(progress["completed"]) == 1
        assert progress["completed"][0]["symbol"] == "sh"

    def test_progress_in_progress(self, session, phoneme):
        record_attempt(session.session_id, "sh", 0.4)
        progress = get_progress(session.session_id)
        assert len(progress["in_progress"]) == 1

    def test_get_attempts_for_phoneme(self, session, phoneme):
        record_attempt(session.session_id, "sh", 0.5)
        record_attempt(session.session_id, "sh", 0.8)
        attempts = get_attempts_for_phoneme(session.session_id, "sh")
        assert len(attempts) == 2
        assert attempts[0].attempt_number == 1
        assert attempts[1].attempt_number == 2
```
