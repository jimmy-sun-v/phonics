import pytest

from apps.ai_tutor.feedback import FeedbackStrategy, determine_feedback_strategy
from apps.phonics.models import Phoneme
from apps.sessions.models import LearningSession
from apps.speech.models import SpeechAttempt


@pytest.mark.django_db
class TestFeedbackStrategy:
    @pytest.fixture
    def session(self):
        return LearningSession.objects.create()

    @pytest.fixture
    def phoneme(self):
        p, _ = Phoneme.objects.get_or_create(symbol="zz", defaults={"category": "digraph", "example_words": ["test"]})
        return p

    def test_first_attempt_high_confidence_encourage(self, session, phoneme):
        ctx = determine_feedback_strategy(session.session_id, "zz", 85)
        assert ctx.strategy == FeedbackStrategy.ENCOURAGE
        assert ctx.attempt_count == 0

    def test_first_attempt_low_confidence_guide(self, session, phoneme):
        ctx = determine_feedback_strategy(session.session_id, "zz", 30)
        assert ctx.strategy == FeedbackStrategy.GUIDE
        assert len(ctx.hints) > 0

    def test_second_attempt_guide(self, session, phoneme):
        SpeechAttempt.objects.create(session=session, phoneme=phoneme, confidence=40, attempt_number=1)
        ctx = determine_feedback_strategy(session.session_id, "zz", 50)
        assert ctx.strategy == FeedbackStrategy.GUIDE

    def test_three_plus_attempts_adjust(self, session, phoneme):
        for i in range(1, 4):
            SpeechAttempt.objects.create(session=session, phoneme=phoneme, confidence=30, attempt_number=i)
        ctx = determine_feedback_strategy(session.session_id, "zz", 40)
        assert ctx.strategy == FeedbackStrategy.ADJUST
        all_hints = " ".join(ctx.hints).lower()
        assert "slowly" in all_hints or "listen" in all_hints

    def test_hints_never_discouraging(self, session, phoneme):
        for i in range(1, 6):
            SpeechAttempt.objects.create(session=session, phoneme=phoneme, confidence=20, attempt_number=i)
        ctx = determine_feedback_strategy(session.session_id, "zz", 20)
        all_hints = " ".join(ctx.hints).lower()
        assert "wrong" not in all_hints
        assert "bad" not in all_hints
        assert "fail" not in all_hints
