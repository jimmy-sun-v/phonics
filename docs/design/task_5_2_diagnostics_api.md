# Design: Task 5.2 – Diagnostics Data API

## Overview

Build JSON API endpoints exposing aggregate diagnostics data: total attempts, average confidence, error rates, phoneme breakdown, and daily trends for the diagnostics dashboard.

## Dependencies

- Task 5.1 (Logging)
- Task 2.3 (SpeechAttempt model)

## Detailed Design

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/speech/diagnostics/summary/` | GET | Overall summary stats |
| `/api/speech/diagnostics/phonemes/` | GET | Per-phoneme metrics |
| `/api/speech/diagnostics/daily/` | GET | Daily activity trend |

### Django Views

**File: `apps/speech/diagnostics_views.py`**

```python
from datetime import timedelta

from django.conf import settings
from django.db.models import Avg, Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.speech.models import SpeechAttempt

CONFIDENCE_THRESHOLD = getattr(settings, "PHONEME_COMPLETION_THRESHOLD", 0.7)


@api_view(["GET"])
def diagnostics_summary(request):
    """Overall diagnostics summary."""
    attempts = SpeechAttempt.objects.all()
    total = attempts.count()

    if total == 0:
        return Response({
            "total_attempts": 0,
            "avg_confidence": 0,
            "correct_rate": 0,
            "total_sessions": 0,
        })

    stats = attempts.aggregate(
        avg_confidence=Avg("confidence"),
        correct_count=Count("id", filter=Q(confidence__gte=CONFIDENCE_THRESHOLD)),
    )

    session_count = attempts.values("session_id").distinct().count()

    return Response({
        "total_attempts": total,
        "avg_confidence": round(stats["avg_confidence"], 3),
        "correct_rate": round(stats["correct_count"] / total, 3),
        "total_sessions": session_count,
    })


@api_view(["GET"])
def diagnostics_by_phoneme(request):
    """Per-phoneme metrics."""
    phoneme_stats = (
        SpeechAttempt.objects
        .values("phoneme__symbol", "phoneme__category")
        .annotate(
            attempts=Count("id"),
            avg_confidence=Avg("confidence"),
            correct_count=Count("id", filter=Q(confidence__gte=CONFIDENCE_THRESHOLD)),
        )
        .order_by("phoneme__category", "phoneme__symbol")
    )

    results = []
    for row in phoneme_stats:
        results.append({
            "phoneme": row["phoneme__symbol"],
            "category": row["phoneme__category"],
            "attempts": row["attempts"],
            "avg_confidence": round(row["avg_confidence"], 3),
            "correct_rate": round(row["correct_count"] / row["attempts"], 3) if row["attempts"] else 0,
        })

    return Response(results)


@api_view(["GET"])
def diagnostics_daily(request):
    """Daily activity for the last 30 days."""
    since = timezone.now() - timedelta(days=30)

    daily = (
        SpeechAttempt.objects
        .filter(created_at__gte=since)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(
            attempts=Count("id"),
            avg_confidence=Avg("confidence"),
        )
        .order_by("day")
    )

    return Response(list(daily))
```

### URL Configuration

```python
# apps/speech/urls.py (add diagnostics routes)
from apps.speech import diagnostics_views

urlpatterns += [
    path("diagnostics/summary/", diagnostics_views.diagnostics_summary),
    path("diagnostics/phonemes/", diagnostics_views.diagnostics_by_phoneme),
    path("diagnostics/daily/", diagnostics_views.diagnostics_daily),
]
```

## Acceptance Criteria

- [ ] `/api/speech/diagnostics/summary/` returns total attempts, avg_confidence, correct_rate, session count
- [ ] `/api/speech/diagnostics/phonemes/` returns per-phoneme breakdown
- [ ] `/api/speech/diagnostics/daily/` returns 30-day daily trend
- [ ] Empty database returns zero/empty gracefully

## Test Strategy

```python
# tests/test_diagnostics_api.py
import pytest
from django.test import Client
from apps.phonics.models import Phoneme
from apps.sessions.models import LearningSession
from apps.speech.models import SpeechAttempt


@pytest.mark.django_db
class TestDiagnosticsAPI:
    def test_summary_empty(self, client):
        resp = client.get("/api/speech/diagnostics/summary/")
        assert resp.status_code == 200
        assert resp.json()["total_attempts"] == 0

    def test_summary_with_data(self, client, speech_attempt_factory):
        speech_attempt_factory.create_batch(5, confidence=0.9)
        speech_attempt_factory.create_batch(5, confidence=0.3)

        resp = client.get("/api/speech/diagnostics/summary/")
        data = resp.json()
        assert data["total_attempts"] == 10
        assert data["correct_rate"] == 0.5

    def test_phonemes_endpoint(self, client, speech_attempt_factory):
        speech_attempt_factory.create(confidence=0.8)
        resp = client.get("/api/speech/diagnostics/phonemes/")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1
```
