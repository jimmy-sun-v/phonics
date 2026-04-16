import pytest
from django.test import Client

from apps.phonics.models import Phoneme
from apps.sessions.models import LearningSession
from apps.speech.models import SpeechAttempt


@pytest.mark.django_db
class TestDiagnosticsSummary:
    def test_summary_empty(self, client):
        resp = client.get("/api/speech/diagnostics/summary/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_attempts"] == 0
        assert data["avg_confidence"] == 0
        assert data["correct_rate"] == 0

    def test_summary_with_data(self, client):
        phoneme = Phoneme.objects.create(
            symbol="zz", category="single_letter",
            example_words=["test"], display_order=999,
        )
        session = LearningSession.objects.create(current_phoneme=phoneme)
        SpeechAttempt.objects.create(
            session=session, phoneme=phoneme, confidence=90, attempt_number=1
        )
        SpeechAttempt.objects.create(
            session=session, phoneme=phoneme, confidence=30, attempt_number=2
        )

        resp = client.get("/api/speech/diagnostics/summary/")
        data = resp.json()
        assert data["total_attempts"] == 2
        assert data["correct_rate"] == 0.5
        assert data["total_sessions"] == 1


@pytest.mark.django_db
class TestDiagnosticsPhonemes:
    def test_phonemes_empty(self, client):
        resp = client.get("/api/speech/diagnostics/phonemes/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_phonemes_with_data(self, client):
        phoneme = Phoneme.objects.create(
            symbol="zz", category="single_letter",
            example_words=["test"], display_order=999,
        )
        session = LearningSession.objects.create(current_phoneme=phoneme)
        SpeechAttempt.objects.create(
            session=session, phoneme=phoneme, confidence=80, attempt_number=1
        )

        resp = client.get("/api/speech/diagnostics/phonemes/")
        data = resp.json()
        assert len(data) == 1
        assert data[0]["phoneme"] == "zz"
        assert data[0]["attempts"] == 1


@pytest.mark.django_db
class TestDiagnosticsDaily:
    def test_daily_empty(self, client):
        resp = client.get("/api/speech/diagnostics/daily/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_daily_with_data(self, client):
        phoneme = Phoneme.objects.create(
            symbol="zz", category="single_letter",
            example_words=["test"], display_order=999,
        )
        session = LearningSession.objects.create(current_phoneme=phoneme)
        SpeechAttempt.objects.create(
            session=session, phoneme=phoneme, confidence=80, attempt_number=1
        )

        resp = client.get("/api/speech/diagnostics/daily/")
        data = resp.json()
        assert len(data) == 1
        assert data[0]["attempts"] == 1
