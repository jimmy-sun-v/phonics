# Design: Task 3.4 – Azure Speech-to-Text Integration Service

## Overview

Create a service wrapper around Azure Speech Services STT. Accepts audio input and returns transcription text with a confidence score.

## Dependencies

- Task 1.7 (Azure Speech key in environment)

## Detailed Design

### Service Module

**File: `apps/speech/azure_client.py`**

```python
import logging
from dataclasses import dataclass
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class STTResult:
    """Structured result from speech-to-text recognition."""
    text: str
    confidence: float
    is_successful: bool
    error_message: str | None = None


def recognize_speech(audio_data: bytes, expected_text: str | None = None) -> STTResult:
    """Send audio to Azure Speech Services and return transcription.

    Args:
        audio_data: Raw audio bytes (WAV format preferred).
        expected_text: Optional expected text for pronunciation assessment.

    Returns:
        STTResult with text, confidence, and status.
    """
    import azure.cognitiveservices.speech as speechsdk

    speech_key = settings.AZURE_SPEECH_KEY
    speech_region = settings.AZURE_SPEECH_REGION

    if not speech_key or not speech_region:
        logger.error("Azure Speech credentials not configured")
        return STTResult(
            text="",
            confidence=0.0,
            is_successful=False,
            error_message="Speech service not configured",
        )

    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=speech_key,
            region=speech_region,
        )
        speech_config.speech_recognition_language = "en-US"

        # Create audio stream from bytes
        audio_stream = speechsdk.audio.PushAudioInputStream()
        audio_stream.write(audio_data)
        audio_stream.close()

        audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_config,
        )

        # Set timeout
        timeout_ms = getattr(settings, "AZURE_SPEECH_TIMEOUT_MS", 5000)
        result = recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            # Extract confidence from detailed results if available
            confidence = _extract_confidence(result)
            return STTResult(
                text=result.text.strip().rstrip("."),
                confidence=confidence,
                is_successful=True,
            )
        elif result.reason == speechsdk.ResultReason.NoMatch:
            return STTResult(
                text="",
                confidence=0.0,
                is_successful=False,
                error_message="No speech recognized",
            )
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            logger.error("Speech recognition canceled: %s", cancellation.reason)
            return STTResult(
                text="",
                confidence=0.0,
                is_successful=False,
                error_message=f"Recognition canceled: {cancellation.reason}",
            )

    except Exception as e:
        logger.exception("Speech recognition error")
        return STTResult(
            text="",
            confidence=0.0,
            is_successful=False,
            error_message=str(e),
        )


def _extract_confidence(result) -> float:
    """Extract confidence score from recognition result.

    Uses the detailed results JSON if available, otherwise defaults to
    a reasonable confidence based on successful recognition.
    """
    import json
    try:
        details = json.loads(result.json)
        if "NBest" in details and len(details["NBest"]) > 0:
            return details["NBest"][0].get("Confidence", 0.8)
    except (json.JSONDecodeError, AttributeError, KeyError):
        pass
    # Default confidence for successful recognition
    return 0.8
```

### Configuration

In `config/settings/base.py`:
```python
AZURE_SPEECH_KEY = env("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = env("AZURE_SPEECH_REGION")
AZURE_SPEECH_TIMEOUT_MS = 5000
```

### Error Handling Strategy

| Scenario | Behavior |
|----------|----------|
| No Azure credentials | Return error STTResult, log error |
| Audio too short/empty | Azure returns NoMatch → return error |
| Network timeout | Exception caught → return error STTResult |
| Azure service error | Cancellation → return error with reason |
| Successful recognition | Return text + confidence |

### Audio Format Notes

- Azure Speech SDK accepts WAV (PCM 16kHz 16-bit mono) natively
- Browser MediaRecorder typically produces WebM/Opus
- Audio conversion (if needed) should be handled at the view layer before calling this service
- Consider adding a utility function for WebM→WAV conversion using `pydub` or `ffmpeg`

## Acceptance Criteria

- [ ] Service calls Azure Speech SDK
- [ ] Returns `STTResult` with text and confidence
- [ ] Missing credentials → structured error, no crash
- [ ] Timeout/network errors → structured error response
- [ ] No unhandled exceptions bubble up

## Test Strategy

**File: `apps/speech/tests/test_services.py`**

```python
import pytest
from unittest.mock import patch, MagicMock
from apps.speech.azure_client import recognize_speech, STTResult


class TestSTTService:
    @patch("apps.speech.azure_client.settings")
    def test_missing_credentials(self, mock_settings):
        mock_settings.AZURE_SPEECH_KEY = ""
        mock_settings.AZURE_SPEECH_REGION = ""
        result = recognize_speech(b"audio_data")
        assert result.is_successful is False
        assert "not configured" in result.error_message

    @patch("azure.cognitiveservices.speech.SpeechRecognizer")
    @patch("apps.speech.azure_client.settings")
    def test_successful_recognition(self, mock_settings, mock_recognizer_cls):
        mock_settings.AZURE_SPEECH_KEY = "test-key"
        mock_settings.AZURE_SPEECH_REGION = "eastus"
        mock_settings.AZURE_SPEECH_TIMEOUT_MS = 5000

        import azure.cognitiveservices.speech as speechsdk
        mock_result = MagicMock()
        mock_result.reason = speechsdk.ResultReason.RecognizedSpeech
        mock_result.text = "ship."
        mock_result.json = '{"NBest": [{"Confidence": 0.92}]}'

        mock_recognizer = MagicMock()
        mock_recognizer.recognize_once.return_value = mock_result
        mock_recognizer_cls.return_value = mock_recognizer

        result = recognize_speech(b"audio_data")
        assert result.is_successful is True
        assert result.text == "ship"
        assert result.confidence == 0.92

    @patch("azure.cognitiveservices.speech.SpeechRecognizer")
    @patch("apps.speech.azure_client.settings")
    def test_no_speech_recognized(self, mock_settings, mock_recognizer_cls):
        mock_settings.AZURE_SPEECH_KEY = "test-key"
        mock_settings.AZURE_SPEECH_REGION = "eastus"
        mock_settings.AZURE_SPEECH_TIMEOUT_MS = 5000

        import azure.cognitiveservices.speech as speechsdk
        mock_result = MagicMock()
        mock_result.reason = speechsdk.ResultReason.NoMatch

        mock_recognizer = MagicMock()
        mock_recognizer.recognize_once.return_value = mock_result
        mock_recognizer_cls.return_value = mock_recognizer

        result = recognize_speech(b"audio_data")
        assert result.is_successful is False
```
