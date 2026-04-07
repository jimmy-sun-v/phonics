from unittest.mock import patch

from apps.speech.tts_service import _build_ssml, synthesize_speech


class TestTTSService:
    @patch("apps.speech.tts_service.settings")
    def test_missing_credentials(self, mock_settings):
        mock_settings.AZURE_SPEECH_KEY = ""
        mock_settings.AZURE_SPEECH_REGION = ""
        result = synthesize_speech("ship")
        assert result.is_successful is False

    def test_ssml_escaping(self):
        ssml = _build_ssml('<script>alert("xss")</script>')
        assert "<script>" not in ssml
        assert "&lt;script&gt;" in ssml

    def test_ssml_structure(self):
        ssml = _build_ssml("ship")
        assert "en-US-AnaNeural" in ssml
        assert 'rate="slow"' in ssml
