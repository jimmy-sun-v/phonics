from unittest.mock import patch

from apps.speech.azure_client import recognize_speech


class TestSTTService:
    @patch("apps.speech.azure_client.settings")
    def test_missing_credentials(self, mock_settings):
        mock_settings.AZURE_SPEECH_KEY = ""
        mock_settings.AZURE_SPEECH_REGION = ""
        result = recognize_speech(b"audio_data")
        assert result.is_successful is False
        assert "not configured" in result.error_message
