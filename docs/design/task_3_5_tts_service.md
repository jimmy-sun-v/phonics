# Design: Task 3.5 – Azure Text-to-Speech Integration Service

## Overview

Create a service wrapper for Azure TTS that converts text (phoneme sounds or words) into audio data suitable for browser playback.

## Dependencies

- Task 1.7 (Azure Speech key in environment)

## Detailed Design

### Service Module

**File: `apps/speech/tts_service.py`**

```python
import logging
from dataclasses import dataclass
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class TTSResult:
    """Structured result from text-to-speech synthesis."""
    audio_data: bytes
    content_type: str
    is_successful: bool
    error_message: str | None = None


def synthesize_speech(text: str) -> TTSResult:
    """Convert text to speech audio using Azure TTS.

    Uses a child-friendly voice (en-US-AnaNeural) optimized for
    clarity and warmth.

    Args:
        text: The text to synthesize (phoneme or word, e.g., "sh", "ship").

    Returns:
        TTSResult with audio bytes and content type.
    """
    import azure.cognitiveservices.speech as speechsdk

    speech_key = settings.AZURE_SPEECH_KEY
    speech_region = settings.AZURE_SPEECH_REGION

    if not speech_key or not speech_region:
        logger.error("Azure Speech credentials not configured")
        return TTSResult(
            audio_data=b"",
            content_type="",
            is_successful=False,
            error_message="Speech service not configured",
        )

    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=speech_key,
            region=speech_region,
        )

        # Child-friendly voice
        speech_config.speech_synthesis_voice_name = "en-US-AnaNeural"

        # Output format suitable for browser playback
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )

        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=None,  # Output to stream, not speaker
        )

        # Use SSML for better pronunciation control
        ssml = _build_ssml(text)
        result = synthesizer.speak_ssml(ssml)

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return TTSResult(
                audio_data=result.audio_data,
                content_type="audio/mpeg",
                is_successful=True,
            )
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            logger.error("TTS canceled: %s", cancellation.reason)
            return TTSResult(
                audio_data=b"",
                content_type="",
                is_successful=False,
                error_message=f"Synthesis canceled: {cancellation.reason}",
            )

    except Exception as e:
        logger.exception("TTS synthesis error")
        return TTSResult(
            audio_data=b"",
            content_type="",
            is_successful=False,
            error_message=str(e),
        )


def _build_ssml(text: str) -> str:
    """Build SSML for controlled pronunciation.

    Uses slow speaking rate for phoneme clarity.
    """
    # Sanitize text to prevent SSML injection
    safe_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    return f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
    <voice name="en-US-AnaNeural">
        <prosody rate="slow" pitch="medium">
            {safe_text}
        </prosody>
    </voice>
</speak>"""
```

### Voice Selection

| Voice | Reason |
|-------|--------|
| `en-US-AnaNeural` | Young female voice, warm and clear. Suitable for children's educational apps. |

Alternative voices: `en-US-JennyNeural` (adult female), `en-US-GuyNeural` (adult male).

### Audio Format

- **Format**: MP3 (16kHz, 32kbps, mono)
- **Content-Type**: `audio/mpeg`
- **Rationale**: MP3 is universally supported in browsers via `<audio>` element and `Audio()` API. Small file size for responsive playback.

### SSML Features

- **`rate="slow"`**: Slower speech for phoneme clarity
- **`pitch="medium"`**: Natural pitch for child audience
- **XML escaping**: Input text is sanitized to prevent SSML injection

## Acceptance Criteria

- [ ] Service generates audio from text input
- [ ] Voice is `en-US-AnaNeural` (child-friendly)
- [ ] Audio format is MP3, playable in browser
- [ ] Missing credentials → structured error
- [ ] SSML injection prevented via text escaping

## Test Strategy

**File: `apps/speech/tests/test_tts.py`**

```python
import pytest
from unittest.mock import patch, MagicMock
from apps.speech.tts_service import synthesize_speech, _build_ssml


class TestTTSService:
    @patch("apps.speech.tts_service.settings")
    def test_missing_credentials(self, mock_settings):
        mock_settings.AZURE_SPEECH_KEY = ""
        mock_settings.AZURE_SPEECH_REGION = ""
        result = synthesize_speech("ship")
        assert result.is_successful is False

    @patch("azure.cognitiveservices.speech.SpeechSynthesizer")
    @patch("apps.speech.tts_service.settings")
    def test_successful_synthesis(self, mock_settings, mock_synth_cls):
        mock_settings.AZURE_SPEECH_KEY = "key"
        mock_settings.AZURE_SPEECH_REGION = "eastus"

        import azure.cognitiveservices.speech as speechsdk
        mock_result = MagicMock()
        mock_result.reason = speechsdk.ResultReason.SynthesizingAudioCompleted
        mock_result.audio_data = b"fake-audio-data"

        mock_synth = MagicMock()
        mock_synth.speak_ssml.return_value = mock_result
        mock_synth_cls.return_value = mock_synth

        result = synthesize_speech("ship")
        assert result.is_successful is True
        assert result.content_type == "audio/mpeg"
        assert len(result.audio_data) > 0

    def test_ssml_escaping(self):
        ssml = _build_ssml('<script>alert("xss")</script>')
        assert "<script>" not in ssml
        assert "&lt;script&gt;" in ssml

    def test_ssml_structure(self):
        ssml = _build_ssml("ship")
        assert "en-US-AnaNeural" in ssml
        assert 'rate="slow"' in ssml
        assert "ship" in ssml
```
