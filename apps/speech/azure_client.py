import io
import logging
import threading
from dataclasses import dataclass

from django.conf import settings
from pydub import AudioSegment

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
        pcm_data = _convert_to_wav(audio_data)

        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        speech_config.speech_recognition_language = "en-US"

        audio_stream = speechsdk.audio.PushAudioInputStream()
        audio_stream.write(pcm_data)
        audio_stream.close()

        audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

        if expected_text:
            pronunciation_config = speechsdk.PronunciationAssessmentConfig(
                reference_text=expected_text,
                grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
                granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
            )

        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        if expected_text:
            pronunciation_config.apply_to(recognizer)

        result = recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            text = result.text.strip().rstrip(".")
            if expected_text:
                confidence = _extract_pronunciation_score(result)
            else:
                confidence = _extract_confidence(result)
            return STTResult(
                text=text,
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


@log_service_call("azure_stt_continuous")
def recognize_speech_continuous(audio_data: bytes) -> STTResult:
    """Transcribe longer audio using continuous recognition.

    Unlike recognize_once(), this captures all utterances across pauses,
    making it suitable for story-length recordings (up to ~30 seconds).
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
        pcm_data = _convert_to_wav(audio_data)

        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        speech_config.speech_recognition_language = "en-US"

        audio_stream = speechsdk.audio.PushAudioInputStream()
        audio_stream.write(pcm_data)
        audio_stream.close()

        audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)
        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        done_event = threading.Event()
        segments: list[str] = []
        errors: list[str] = []

        def on_recognized(evt):
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                text = evt.result.text.strip()
                if text:
                    segments.append(text)

        def on_canceled(evt):
            if evt.cancellation_details.reason == speechsdk.CancellationReason.Error:
                errors.append(str(evt.cancellation_details.error_details))
            done_event.set()

        def on_session_stopped(evt):
            done_event.set()

        recognizer.recognized.connect(on_recognized)
        recognizer.canceled.connect(on_canceled)
        recognizer.session_stopped.connect(on_session_stopped)

        recognizer.start_continuous_recognition()
        done_event.wait(timeout=60)
        recognizer.stop_continuous_recognition()

        if errors:
            logger.error("Continuous recognition error: %s", errors[0])
            return STTResult(
                text="",
                confidence=0.0,
                is_successful=False,
                error_message=errors[0],
            )

        if not segments:
            return STTResult(
                text="",
                confidence=0.0,
                is_successful=False,
                error_message="No speech recognized",
            )

        full_text = " ".join(segments)
        return STTResult(text=full_text, confidence=1.0, is_successful=True)

    except Exception as e:
        logger.exception("Continuous speech recognition error")
        return STTResult(text="", confidence=0.0, is_successful=False, error_message=str(e))


def _convert_to_wav(audio_data: bytes) -> bytes:
    """Convert audio (e.g. WebM/Opus) to 16-bit 16kHz mono PCM WAV for Azure Speech SDK."""
    audio_file = io.BytesIO(audio_data)
    segment = AudioSegment.from_file(audio_file)
    segment = segment.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    wav_buffer = io.BytesIO()
    segment.export(wav_buffer, format="wav")
    return wav_buffer.getvalue()


def _extract_pronunciation_score(result) -> float:
    """Extract the PronunciationScore (0-100) from Pronunciation Assessment result."""
    import json

    try:
        details = json.loads(result.json)
        if "NBest" in details and len(details["NBest"]) > 0:
            pron_assessment = details["NBest"][0].get("PronunciationAssessment", {})
            return pron_assessment.get("PronScore", 0.0)
    except (json.JSONDecodeError, AttributeError, KeyError):
        logger.warning("Failed to extract pronunciation score from result")
    return 0.0


def _extract_confidence(result) -> float:
    import json

    try:
        details = json.loads(result.json)
        if "NBest" in details and len(details["NBest"]) > 0:
            return details["NBest"][0].get("Confidence", 0.8)
    except (json.JSONDecodeError, AttributeError, KeyError):
        pass
    return 0.8
