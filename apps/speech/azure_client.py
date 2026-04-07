import logging
from dataclasses import dataclass

from django.conf import settings

from apps.speech.logging_config import log_service_call

logger = logging.getLogger(__name__)


@dataclass
class STTResult:
    text: str
    confidence: float
    is_successful: bool
    error_message: str | None = None


@log_service_call("azure_stt")
def recognize_speech(audio_data: bytes, expected_text: str | None = None) -> STTResult:
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
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        speech_config.speech_recognition_language = "en-US"

        audio_stream = speechsdk.audio.PushAudioInputStream()
        audio_stream.write(audio_data)
        audio_stream.close()

        audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)
        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        result = recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
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
        return STTResult(text="", confidence=0.0, is_successful=False, error_message=str(e))


def _extract_confidence(result) -> float:
    import json

    try:
        details = json.loads(result.json)
        if "NBest" in details and len(details["NBest"]) > 0:
            return details["NBest"][0].get("Confidence", 0.8)
    except (json.JSONDecodeError, AttributeError, KeyError):
        pass
    return 0.8
