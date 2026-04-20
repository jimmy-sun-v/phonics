from unittest.mock import patch

import pytest

from apps.speech.azure_client import STTResult


@pytest.mark.django_db
class TestTranscribeAPI:
    def test_missing_audio(self, client):
        response = client.post(
            "/api/speech/transcribe/",
            {},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_invalid_base64(self, client):
        response = client.post(
            "/api/speech/transcribe/",
            {"audio": "not-valid-base64!!!"},
            content_type="application/json",
        )
        assert response.status_code == 400

    @patch("apps.speech.views.recognize_speech_continuous")
    def test_successful_transcription(self, mock_stt, client):
        mock_stt.return_value = STTResult(
            text="Once upon a time",
            confidence=1.0,
            is_successful=True,
        )
        response = client.post(
            "/api/speech/transcribe/",
            {"audio": "AAAA"},  # minimal valid base64
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Once upon a time"
        assert data["is_successful"] is True

    @patch("apps.speech.views.recognize_speech_continuous")
    def test_failed_transcription(self, mock_stt, client):
        mock_stt.return_value = STTResult(
            text="",
            confidence=0,
            is_successful=False,
            error_message="No speech recognized",
        )
        response = client.post(
            "/api/speech/transcribe/",
            {"audio": "AAAA"},
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_successful"] is False
