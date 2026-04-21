import logging
import time

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.ai_tutor.feedback import determine_feedback_strategy
from apps.ai_tutor.llm_client import call_llm
from apps.ai_tutor.services import render_prompt
from apps.ai_tutor.validators import validate_response
from apps.phonics.models import Phoneme
from apps.sessions.progress import record_attempt
from apps.speech.azure_client import recognize_speech, recognize_speech_continuous
from apps.speech.error_detection import detect_error
from apps.speech.serializers import SpeechAttemptRequestSerializer, SpeechAttemptResponseSerializer
from apps.speech.tts_service import synthesize_speech

logger = logging.getLogger(__name__)

FALLBACK_FEEDBACK = "Great try! Let's practice that sound again!"


@api_view(["POST"])
def speech_attempt(request):
    start_time = time.monotonic()

    serializer = SpeechAttemptRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    session_id = serializer.validated_data["session_id"]
    phoneme_symbol = serializer.validated_data["phoneme"]
    audio_bytes = serializer.validated_data["audio"]

    # Use the first example word as reference text for pronunciation assessment,
    # since the UI instructs the child to say the example word (e.g. "bat"), not
    # the raw phoneme symbol (e.g. "b").
    try:
        phoneme_obj = Phoneme.objects.get(symbol=phoneme_symbol)
        reference_text = phoneme_obj.example_words[0] if phoneme_obj.example_words else phoneme_symbol
    except Phoneme.DoesNotExist:
        reference_text = phoneme_symbol

    stt_result = recognize_speech(audio_bytes, expected_text=reference_text)
    if not stt_result.is_successful:
        logger.warning("STT failed for session %s: %s", session_id, stt_result.error_message)
        return Response(
            SpeechAttemptResponseSerializer(
                {
                    "confidence": 0.0,
                    "is_correct": False,
                    "feedback": "I couldn't hear you clearly. Let's try again!",
                    "detected_error": None,
                    "attempt_number": 0,
                }
            ).data,
            status=status.HTTP_200_OK,
        )

    error_result = detect_error(phoneme_symbol, stt_result.text, stt_result.confidence)

    attempt = record_attempt(
        session_id=session_id,
        phoneme_symbol=phoneme_symbol,
        confidence=stt_result.confidence,
        error=error_result.detected_error,
    )

    feedback_ctx = determine_feedback_strategy(
        session_id=session_id,
        phoneme_symbol=phoneme_symbol,
        current_confidence=stt_result.confidence,
    )

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

    elapsed_ms = (time.monotonic() - start_time) * 1000
    logger.info(
        "Speech attempt processed: session=%s phoneme=%s confidence=%.2f correct=%s time=%.0fms",
        session_id,
        phoneme_symbol,
        stt_result.confidence,
        error_result.is_correct,
        elapsed_ms,
    )

    response_data = {
        "confidence": stt_result.confidence,
        "is_correct": error_result.is_correct,
        "feedback": feedback,
        "detected_error": error_result.detected_error,
        "attempt_number": attempt.attempt_number,
    }

    return Response(SpeechAttemptResponseSerializer(response_data).data, status=status.HTTP_200_OK)


@api_view(["GET"])
def text_to_speech(request):
    text = request.query_params.get("text", "").strip()
    if not text:
        return Response({"error": "Missing 'text' query parameter"}, status=status.HTTP_400_BAD_REQUEST)
    if len(text) > 10000:
        return Response({"error": "Text exceeds maximum length (10000 characters)"}, status=status.HTTP_400_BAD_REQUEST)

    result = synthesize_speech(text)
    if not result.is_successful:
        return Response({"error": "Failed to generate audio"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    response = HttpResponse(result.audio_data, content_type=result.content_type)
    response["Content-Length"] = len(result.audio_data)
    response["Cache-Control"] = "public, max-age=3600"
    return response


@api_view(["GET"])
def text_to_speech_with_words(request):
    """TTS that returns audio (base64) and word boundary timings for highlighting."""
    import base64

    text = request.query_params.get("text", "").strip()
    if not text:
        return Response({"error": "Missing 'text' query parameter"}, status=status.HTTP_400_BAD_REQUEST)
    if len(text) > 10000:
        return Response({"error": "Text exceeds maximum length (10000 characters)"}, status=status.HTTP_400_BAD_REQUEST)

    result = synthesize_speech(text)
    if not result.is_successful:
        return Response({"error": "Failed to generate audio"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response({
        "audio_base64": base64.b64encode(result.audio_data).decode("ascii"),
        "content_type": result.content_type,
        "word_boundaries": result.word_boundaries or [],
    })


@api_view(["POST"])
def transcribe(request):
    """Transcribe audio to text using standard STT (no pronunciation assessment)."""
    audio_b64 = request.data.get("audio", "")
    if not audio_b64:
        return Response({"error": "Missing 'audio' field"}, status=status.HTTP_400_BAD_REQUEST)

    import base64

    try:
        audio_bytes = base64.b64decode(audio_b64)
    except Exception:
        return Response({"error": "Invalid base64 audio data"}, status=status.HTTP_400_BAD_REQUEST)

    if len(audio_bytes) > 5 * 1024 * 1024:
        return Response({"error": "Audio data exceeds 5 MB"}, status=status.HTTP_400_BAD_REQUEST)

    stt_result = recognize_speech_continuous(audio_bytes)
    if not stt_result.is_successful:
        return Response({"text": "", "is_successful": False}, status=status.HTTP_200_OK)

    return Response({"text": stt_result.text, "is_successful": True}, status=status.HTTP_200_OK)
