# Design: Task 3.13 – Speech REST API – Submit Attempt Endpoint

## Overview

Create the orchestration endpoint that accepts audio + session + phoneme, processes through STT → error detection → progress recording → AI feedback, and returns the result.

## Dependencies

- Task 3.4 (STT service), Task 3.6 (Error detection), Task 3.3 (Progress tracking)
- Task 3.10 (Feedback strategy), Task 3.7 (Prompt rendering), Task 3.8 (LLM client)
- Task 3.9 (Safety validator)

## Detailed Design

### URL Endpoint

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/speech/attempt/` | Submit speech attempt for evaluation |

### Request Format

```json
{
    "session_id": "uuid-string",
    "phoneme": "sh",
    "audio": "<base64-encoded-audio>"
}
```

### Serializers

**File: `apps/speech/serializers.py`**

```python
import base64
from rest_framework import serializers


class SpeechAttemptRequestSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    phoneme = serializers.CharField(max_length=10)
    audio = serializers.CharField(
        help_text="Base64-encoded audio data",
    )

    def validate_audio(self, value):
        """Validate and decode base64 audio."""
        try:
            audio_bytes = base64.b64decode(value)
        except Exception:
            raise serializers.ValidationError("Invalid base64-encoded audio data")

        # Enforce max size (5 MB)
        max_size = 5 * 1024 * 1024
        if len(audio_bytes) > max_size:
            raise serializers.ValidationError("Audio data exceeds maximum size (5 MB)")

        if len(audio_bytes) == 0:
            raise serializers.ValidationError("Audio data is empty")

        return audio_bytes


class SpeechAttemptResponseSerializer(serializers.Serializer):
    confidence = serializers.FloatField()
    is_correct = serializers.BooleanField()
    feedback = serializers.CharField()
    detected_error = serializers.CharField(allow_null=True)
    attempt_number = serializers.IntegerField()
```

### View — Orchestration Pipeline

**File: `apps/speech/views.py`**

```python
import logging
import time
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.speech.serializers import (
    SpeechAttemptRequestSerializer,
    SpeechAttemptResponseSerializer,
)
from apps.speech.azure_client import recognize_speech
from apps.speech.error_detection import detect_error
from apps.sessions.progress import record_attempt
from apps.ai_tutor.feedback import determine_feedback_strategy
from apps.ai_tutor.services import render_prompt
from apps.ai_tutor.llm_client import call_llm
from apps.ai_tutor.validators import validate_response

logger = logging.getLogger(__name__)

FALLBACK_FEEDBACK = "Great try! Let's practice that sound again!"


@api_view(["POST"])
def speech_attempt(request):
    """Process a speech attempt through the full pipeline.

    Pipeline:
    1. Validate input (session_id, phoneme, audio)
    2. STT: Convert audio → text + confidence
    3. Error detection: Compare expected vs actual
    4. Record attempt in database
    5. Determine feedback strategy
    6. Render AI prompt
    7. Call LLM for feedback
    8. Validate and return safe feedback
    """
    start_time = time.monotonic()

    serializer = SpeechAttemptRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    session_id = serializer.validated_data["session_id"]
    phoneme_symbol = serializer.validated_data["phoneme"]
    audio_bytes = serializer.validated_data["audio"]

    # Step 1: Speech-to-Text
    stt_result = recognize_speech(audio_bytes)
    if not stt_result.is_successful:
        logger.warning("STT failed for session %s: %s", session_id, stt_result.error_message)
        return Response(
            SpeechAttemptResponseSerializer({
                "confidence": 0.0,
                "is_correct": False,
                "feedback": "I couldn't hear you clearly. Let's try again!",
                "detected_error": None,
                "attempt_number": 0,
            }).data,
            status=status.HTTP_200_OK,
        )

    # Step 2: Error Detection
    error_result = detect_error(phoneme_symbol, stt_result.text, stt_result.confidence)

    # Step 3: Record Attempt
    attempt = record_attempt(
        session_id=session_id,
        phoneme_symbol=phoneme_symbol,
        confidence=stt_result.confidence,
        error=error_result.detected_error,
    )

    # Step 4: Determine Feedback Strategy
    feedback_ctx = determine_feedback_strategy(
        session_id=session_id,
        phoneme_symbol=phoneme_symbol,
        current_confidence=stt_result.confidence,
    )

    # Step 5: Render Prompt & Call LLM
    try:
        messages = render_prompt(
            phoneme=phoneme_symbol,
            confidence=stt_result.confidence,
            error=error_result.detected_error,
            attempts=feedback_ctx.attempt_count,
        )
        llm_response = call_llm(messages)

        if llm_response.is_successful:
            feedback = validate_response(llm_response.text)
        else:
            feedback = FALLBACK_FEEDBACK
    except Exception:
        logger.exception("AI feedback generation failed")
        feedback = FALLBACK_FEEDBACK

    # Log response time
    elapsed_ms = (time.monotonic() - start_time) * 1000
    logger.info(
        "Speech attempt processed: session=%s phoneme=%s confidence=%.2f correct=%s time=%.0fms",
        session_id, phoneme_symbol, stt_result.confidence, error_result.is_correct, elapsed_ms,
    )

    response_data = {
        "confidence": stt_result.confidence,
        "is_correct": error_result.is_correct,
        "feedback": feedback,
        "detected_error": error_result.detected_error,
        "attempt_number": attempt.attempt_number,
    }

    return Response(
        SpeechAttemptResponseSerializer(response_data).data,
        status=status.HTTP_200_OK,
    )
```

### URLs

**File: `apps/speech/urls.py`** (add to existing):

```python
from django.urls import path
from . import views

app_name = "speech"

urlpatterns = [
    path("attempt/", views.speech_attempt, name="speech-attempt"),
]
```

### Pipeline Flow Diagram

```
Client Audio (base64)
    ↓
[1] Validate Input
    ↓
[2] Azure STT → {text, confidence}
    ↓
[3] Error Detection → {is_correct, detected_error}
    ↓
[4] Record Attempt → DB (SpeechAttempt)
    ↓
[5] Feedback Strategy → {strategy, hints}
    ↓
[6] Render Prompt → LLM messages
    ↓
[7] Azure OpenAI → raw feedback text
    ↓
[8] Safety Validator → safe feedback text
    ↓
JSON Response
```

### Error Handling

| Failure Point | Behavior |
|---------------|----------|
| Invalid input | 400 with validation errors |
| STT fails | Return friendly "I couldn't hear you" message |
| Error detection fails | Use default (is_correct=False) |
| LLM fails | Use FALLBACK_FEEDBACK |
| Validator rejects | Use FALLBACK_FEEDBACK |

The endpoint **always returns 200** with feedback (never a 500) — the child should always see an encouraging response.

## Acceptance Criteria

- [ ] End-to-end: audio → STT → error detection → progress → AI feedback
- [ ] Response includes confidence, is_correct, feedback, detected_error, attempt_number
- [ ] Response time logged
- [ ] STT failure → friendly error feedback (not HTTP error)
- [ ] LLM failure → fallback feedback
- [ ] Attempt recorded in database
- [ ] Invalid input → 400

## Test Strategy

**File: `apps/speech/tests/test_api.py`**

```python
import base64
import pytest
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from apps.sessions.models import LearningSession
from apps.phonics.models import Phoneme
from apps.speech.azure_client import STTResult


@pytest.mark.django_db
class TestSpeechAttemptAPI:
    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def session(self):
        return LearningSession.objects.create()

    @pytest.fixture
    def phoneme(self):
        return Phoneme.objects.create(symbol="sh", category="digraph", example_words=["ship"])

    @patch("apps.speech.views.call_llm")
    @patch("apps.speech.views.recognize_speech")
    def test_successful_attempt(self, mock_stt, mock_llm, client, session, phoneme):
        mock_stt.return_value = STTResult(text="ship", confidence=0.85, is_successful=True)
        mock_llm.return_value = MagicMock(is_successful=True, text="Great job!")

        audio = base64.b64encode(b"fake-audio").decode()
        response = client.post(
            "/api/speech/attempt/",
            {"session_id": str(session.session_id), "phoneme": "sh", "audio": audio},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["is_correct"] is True
        assert response.data["confidence"] == 0.85
        assert "feedback" in response.data

    @patch("apps.speech.views.recognize_speech")
    def test_stt_failure_returns_friendly_message(self, mock_stt, client, session, phoneme):
        mock_stt.return_value = STTResult(text="", confidence=0.0, is_successful=False, error_message="No speech")

        audio = base64.b64encode(b"silence").decode()
        response = client.post(
            "/api/speech/attempt/",
            {"session_id": str(session.session_id), "phoneme": "sh", "audio": audio},
            format="json",
        )
        assert response.status_code == 200
        assert "couldn't hear" in response.data["feedback"].lower()

    def test_missing_audio_returns_400(self, client, session, phoneme):
        response = client.post(
            "/api/speech/attempt/",
            {"session_id": str(session.session_id), "phoneme": "sh"},
            format="json",
        )
        assert response.status_code == 400
```
