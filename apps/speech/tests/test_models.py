import pytest
from django.core.exceptions import ValidationError

from apps.phonics.models import Phoneme
from apps.sessions.models import LearningSession
from apps.speech.models import SpeechAttempt


@pytest.mark.django_db
class TestSpeechAttemptModel:
    @pytest.fixture
    def session(self):
        return LearningSession.objects.create()

    @pytest.fixture
    def phoneme(self):
        return Phoneme.objects.create(symbol="zz", category="digraph", example_words=["test"])

    def test_create_attempt(self, session, phoneme):
        attempt = SpeechAttempt.objects.create(session=session, phoneme=phoneme, confidence=85, attempt_number=1)
        assert attempt.pk is not None
        assert attempt.confidence == 85

    def test_confidence_out_of_range_rejected(self, session, phoneme):
        attempt = SpeechAttempt(session=session, phoneme=phoneme, confidence=150, attempt_number=1)
        with pytest.raises(ValidationError):
            attempt.full_clean()

    def test_confidence_negative_rejected(self, session, phoneme):
        attempt = SpeechAttempt(session=session, phoneme=phoneme, confidence=-1, attempt_number=1)
        with pytest.raises(ValidationError):
            attempt.full_clean()

    def test_cascade_on_session_delete(self, session, phoneme):
        SpeechAttempt.objects.create(session=session, phoneme=phoneme, confidence=50, attempt_number=1)
        session.delete()
        assert SpeechAttempt.objects.count() == 0

    def test_cascade_on_phoneme_delete(self, session, phoneme):
        SpeechAttempt.objects.create(session=session, phoneme=phoneme, confidence=50, attempt_number=1)
        phoneme.delete()
        assert SpeechAttempt.objects.count() == 0

    def test_detected_error_nullable(self, session, phoneme):
        attempt = SpeechAttempt.objects.create(
            session=session, phoneme=phoneme, confidence=90, attempt_number=1, detected_error=None
        )
        assert attempt.detected_error is None
