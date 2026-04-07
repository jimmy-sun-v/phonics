# Design: Task 3.14 – Text-to-Speech REST API Endpoint

## Overview

Create an API endpoint that accepts text and returns audio data for browser playback.

## Dependencies

- Task 3.5 (TTS service)

## Detailed Design

### URL Endpoint

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/speech/tts/?text=ship` | Generate audio for given text |

### View

**File: `apps/speech/views.py`** (add to existing)

```python
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.speech.tts_service import synthesize_speech


@api_view(["GET"])
def text_to_speech(request):
    """Generate audio from text for browser playback.

    Query Parameters:
        text: The text to synthesize (required, max 100 chars)

    Returns:
        Audio binary response with appropriate content type.
    """
    text = request.query_params.get("text", "").strip()

    if not text:
        return Response(
            {"error": "Missing 'text' query parameter"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(text) > 100:
        return Response(
            {"error": "Text exceeds maximum length (100 characters)"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    result = synthesize_speech(text)

    if not result.is_successful:
        return Response(
            {"error": "Failed to generate audio"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    response = HttpResponse(
        result.audio_data,
        content_type=result.content_type,
    )
    response["Content-Length"] = len(result.audio_data)
    response["Cache-Control"] = "public, max-age=3600"  # Cache for 1 hour
    return response
```

### URLs

**File: `apps/speech/urls.py`** (add to existing):

```python
urlpatterns = [
    path("attempt/", views.speech_attempt, name="speech-attempt"),
    path("tts/", views.text_to_speech, name="text-to-speech"),
]
```

### Response Details

- **Content-Type**: `audio/mpeg` (MP3 format)
- **Cache-Control**: `public, max-age=3600` — phoneme audio is static and cacheable
- **Content-Length**: Set for proper download/streaming

### Client-Side Usage

```javascript
// In browser JavaScript:
const audio = new Audio(`/api/speech/tts/?text=${encodeURIComponent('ship')}`);
audio.play();
```

### Input Validation

| Check | Limit | Response |
|-------|-------|----------|
| Missing text | — | 400 |
| Empty text | — | 400 |
| Text too long | > 100 chars | 400 |
| TTS service failure | — | 503 |

### Security

- Text input is limited to 100 characters (prevents abuse)
- SSML injection prevented in the TTS service layer (Task 3.5)
- No user-provided HTML or scripts in the text parameter

## Acceptance Criteria

- [ ] `GET /api/speech/tts/?text=ship` returns audio with `audio/mpeg` content type
- [ ] Missing `text` → 400
- [ ] Empty `text` → 400
- [ ] Text > 100 chars → 400
- [ ] TTS failure → 503
- [ ] Audio playable in browser `<audio>` element
- [ ] Response is cached (Cache-Control header)

## Test Strategy

**File: `apps/speech/tests/test_tts_api.py`**

```python
import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from apps.speech.tts_service import TTSResult


class TestTTSAPI:
    @pytest.fixture
    def client(self):
        return APIClient()

    @patch("apps.speech.views.synthesize_speech")
    def test_successful_tts(self, mock_tts, client):
        mock_tts.return_value = TTSResult(
            audio_data=b"fake-mp3-data",
            content_type="audio/mpeg",
            is_successful=True,
        )
        response = client.get("/api/speech/tts/?text=ship")
        assert response.status_code == 200
        assert response["Content-Type"] == "audio/mpeg"
        assert response.content == b"fake-mp3-data"

    def test_missing_text(self, client):
        response = client.get("/api/speech/tts/")
        assert response.status_code == 400

    def test_empty_text(self, client):
        response = client.get("/api/speech/tts/?text=")
        assert response.status_code == 400

    def test_text_too_long(self, client):
        response = client.get(f"/api/speech/tts/?text={'a' * 101}")
        assert response.status_code == 400

    @patch("apps.speech.views.synthesize_speech")
    def test_tts_failure(self, mock_tts, client):
        mock_tts.return_value = TTSResult(
            audio_data=b"", content_type="", is_successful=False, error_message="Service error"
        )
        response = client.get("/api/speech/tts/?text=ship")
        assert response.status_code == 503
```
