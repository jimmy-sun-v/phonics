import logging
from dataclasses import dataclass

from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class TTSResult:
    audio_data: bytes
    content_type: str
    is_successful: bool
    error_message: str | None = None


def synthesize_speech(text: str) -> TTSResult:
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
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        speech_config.speech_synthesis_voice_name = "en-US-AnaNeural"
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )

        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

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
        return TTSResult(audio_data=b"", content_type="", is_successful=False, error_message=str(e))


def _build_ssml(text: str) -> str:
    safe_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    return f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
    <voice name="en-US-AnaNeural">
        <prosody rate="slow" pitch="medium">
            {safe_text}
        </prosody>
    </voice>
</speak>"""
