# Design: Task 3.12 – Session REST API – Create & Retrieve Endpoints

## Overview

Create API endpoints for creating, retrieving, and updating anonymous learning sessions.

## Dependencies

- Task 3.2 (Session management service)

## Detailed Design

### URL Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/sessions/` | Create new anonymous session |
| GET | `/api/sessions/{session_id}/` | Retrieve session with progress |
| PATCH | `/api/sessions/{session_id}/` | Update current phoneme |

### Serializers

**File: `apps/sessions/serializers.py`**

```python
from rest_framework import serializers
from apps.sessions.models import LearningSession


class SessionCreateSerializer(serializers.Serializer):
    """No input fields required — session is auto-generated."""
    pass


class SessionResponseSerializer(serializers.ModelSerializer):
    current_phoneme_symbol = serializers.CharField(
        source="current_phoneme.symbol",
        read_only=True,
        default=None,
    )
    progress = serializers.SerializerMethodField()

    class Meta:
        model = LearningSession
        fields = [
            "session_id",
            "current_phoneme_symbol",
            "started_at",
            "last_active_at",
            "is_active",
            "progress",
        ]
        read_only_fields = fields

    def get_progress(self, obj):
        from apps.sessions.progress import get_progress
        try:
            return get_progress(obj.session_id)
        except Exception:
            return None


class SessionUpdateSerializer(serializers.Serializer):
    phoneme = serializers.CharField(
        max_length=10,
        help_text="Phoneme symbol to set as current (e.g., 'sh')",
    )
```

### Views

**File: `apps/sessions/views.py`**

```python
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.sessions.serializers import (
    SessionResponseSerializer,
    SessionUpdateSerializer,
)
from apps.sessions.services import (
    create_session,
    get_session,
    update_current_phoneme,
    SessionNotFoundError,
    SessionInactiveError,
)


@api_view(["POST"])
def session_create(request):
    """Create a new anonymous learning session."""
    session = create_session()
    serializer = SessionResponseSerializer(session)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH"])
def session_detail(request, session_id):
    """Retrieve or update a learning session."""
    if request.method == "GET":
        try:
            session = get_session(session_id)
        except SessionNotFoundError:
            return Response(
                {"error": "Session not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = SessionResponseSerializer(session)
        return Response(serializer.data)

    elif request.method == "PATCH":
        serializer = SessionUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = update_current_phoneme(
                session_id, serializer.validated_data["phoneme"]
            )
        except SessionNotFoundError:
            return Response(
                {"error": "Session not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except SessionInactiveError:
            return Response(
                {"error": "Session is no longer active"},
                status=status.HTTP_409_CONFLICT,
            )
        except Exception:
            return Response(
                {"error": "Invalid phoneme"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = SessionResponseSerializer(session)
        return Response(response_serializer.data)
```

### URLs

**File: `apps/sessions/urls.py`**

```python
from django.urls import path
from . import views

app_name = "learning_sessions"

urlpatterns = [
    path("", views.session_create, name="session-create"),
    path("<uuid:session_id>/", views.session_detail, name="session-detail"),
]
```

### Sample API Responses

**POST /api/sessions/** → 201
```json
{
    "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "current_phoneme_symbol": null,
    "started_at": "2026-04-02T10:00:00Z",
    "last_active_at": "2026-04-02T10:00:00Z",
    "is_active": true,
    "progress": {
        "completed": [],
        "in_progress": [],
        "remaining": [...],
        "total_phonemes": 59,
        "completed_count": 0,
        "completion_percentage": 0.0
    }
}
```

### Security

- No PII fields accepted or returned (no name, email, etc.)
- Session ID is a UUID — non-sequential, non-guessable
- No authentication required (anonymous sessions by design)

## Acceptance Criteria

- [ ] POST creates session → 201 with UUID
- [ ] GET with valid UUID → 200 with progress
- [ ] GET with invalid UUID → 404
- [ ] PATCH updates current_phoneme
- [ ] PATCH on inactive session → 409
- [ ] No PII in any request or response

## Test Strategy

**File: `apps/sessions/tests/test_api.py`**

```python
import pytest
from rest_framework.test import APIClient
from apps.sessions.models import LearningSession
from apps.phonics.models import Phoneme


@pytest.mark.django_db
class TestSessionAPI:
    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture(autouse=True)
    def setup_phoneme(self):
        Phoneme.objects.create(symbol="sh", category="digraph", example_words=["ship"])

    def test_create_session(self, client):
        response = client.post("/api/sessions/")
        assert response.status_code == 201
        assert "session_id" in response.data

    def test_get_session(self, client):
        response = client.post("/api/sessions/")
        session_id = response.data["session_id"]
        response = client.get(f"/api/sessions/{session_id}/")
        assert response.status_code == 200

    def test_get_invalid_session(self, client):
        response = client.get("/api/sessions/00000000-0000-0000-0000-000000000000/")
        assert response.status_code == 404

    def test_update_phoneme(self, client):
        response = client.post("/api/sessions/")
        session_id = response.data["session_id"]
        response = client.patch(
            f"/api/sessions/{session_id}/",
            {"phoneme": "sh"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["current_phoneme_symbol"] == "sh"
```
