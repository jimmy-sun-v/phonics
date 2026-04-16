import pytest

from apps.phonics.models import Phoneme
from apps.sessions.models import LearningSession
from apps.sessions.progress import get_attempts_for_phoneme, get_progress, record_attempt


@pytest.mark.django_db
class TestProgressTracking:
    @pytest.fixture
    def session(self):
        return LearningSession.objects.create()

    @pytest.fixture
    def phoneme(self):
        p, _ = Phoneme.objects.get_or_create(symbol="zz", defaults={"category": "digraph", "example_words": ["test"]})
        return p

    def test_record_attempt_auto_increments(self, session, phoneme):
        a1 = record_attempt(session.session_id, "zz", 50)
        a2 = record_attempt(session.session_id, "zz", 70)
        a3 = record_attempt(session.session_id, "zz", 90)
        assert a1.attempt_number == 1
        assert a2.attempt_number == 2
        assert a3.attempt_number == 3

    def test_get_attempts_for_phoneme(self, session, phoneme):
        record_attempt(session.session_id, "zz", 50)
        record_attempt(session.session_id, "zz", 70)
        attempts = get_attempts_for_phoneme(session.session_id, "zz")
        assert len(attempts) == 2

    def test_get_progress(self, session, phoneme):
        record_attempt(session.session_id, "zz", 90)
        progress = get_progress(session.session_id)
        assert progress["completed_count"] >= 1
        assert progress["total_phonemes"] > 0
