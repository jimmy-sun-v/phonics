from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from apps.speech.tts_service import TTSResult


class TestTTSAPI:
    @pytest.fixture
    def client(self):
        return APIClient()

    @patch("apps.speech.views.synthesize_speech")
    def test_successful_tts(self, mock_tts, client):
        mock_tts.return_value = TTSResult(audio_data=b"fake-mp3-data", content_type="audio/mpeg", is_successful=True)
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
        response = client.get(f"/api/speech/tts/?text={'a' * 10001}")
        assert response.status_code == 400

    @patch("apps.speech.views.synthesize_speech")
    def test_tts_failure(self, mock_tts, client):
        mock_tts.return_value = TTSResult(audio_data=b"", content_type="", is_successful=False, error_message="Error")
        response = client.get("/api/speech/tts/?text=ship")
        assert response.status_code == 503
