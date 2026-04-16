import pytest
from unittest.mock import patch

from apps.ai_tutor.validators import (
    validate_response,
    FORBIDDEN_WORDS,
    FALLBACK_MESSAGES,
)
from apps.ai_tutor.feedback import (
    FeedbackStrategy,
    determine_feedback_strategy,
)


class TestSafetyValidator:
    @pytest.mark.parametrize("response", [
        "Great job saying that sound!",
        "Try again, you're doing well!",
        "Almost there! Let's try once more.",
    ])
    def test_safe_responses_pass_through(self, response):
        result = validate_response(response)
        assert result == response

    @pytest.mark.parametrize("response", [
        "You stupid child",
        "That was dumb",
    ])
    def test_forbidden_words_blocked(self, response):
        result = validate_response(response)
        assert result in FALLBACK_MESSAGES

    def test_empty_response_gets_fallback(self):
        result = validate_response("")
        assert result in FALLBACK_MESSAGES

    def test_none_response_gets_fallback(self):
        result = validate_response(None)
        assert result in FALLBACK_MESSAGES

    def test_whitespace_only_gets_fallback(self):
        result = validate_response("   ")
        assert result in FALLBACK_MESSAGES

    def test_fallback_messages_are_encouraging(self):
        negative_words = {"wrong", "bad", "stupid", "dumb", "fail", "terrible", "awful"}
        for msg in FALLBACK_MESSAGES:
            words = set(msg.lower().split())
            assert not words & negative_words, f"Fallback contains negative word: {msg}"

    def test_all_forbidden_words_detected(self):
        for word in FORBIDDEN_WORDS:
            result = validate_response(f"You are {word} at this")
            assert result in FALLBACK_MESSAGES, f"Forbidden word '{word}' was not blocked"

    def test_personal_question_blocked(self):
        result = validate_response("What is your name?")
        assert result in FALLBACK_MESSAGES

    def test_long_response_truncated(self):
        long_text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        result = validate_response(long_text)
        assert result.count(".") <= 2


class TestFeedbackStrategy:
    @patch("apps.ai_tutor.feedback.get_attempts_for_phoneme", return_value=[])
    def test_first_attempt_high_confidence_encourages(self, mock_attempts):
        ctx = determine_feedback_strategy("fake-id", "sh", 80)
        assert ctx.strategy == FeedbackStrategy.ENCOURAGE

    @patch("apps.ai_tutor.feedback.get_attempts_for_phoneme", return_value=[])
    def test_first_attempt_low_confidence_guides(self, mock_attempts):
        ctx = determine_feedback_strategy("fake-id", "sh", 30)
        assert ctx.strategy == FeedbackStrategy.GUIDE

    @patch("apps.ai_tutor.feedback.get_attempts_for_phoneme")
    def test_many_attempts_adjusts(self, mock_attempts):
        class FakeAttempt:
            confidence = 20
        mock_attempts.return_value = [FakeAttempt(), FakeAttempt(), FakeAttempt()]
        ctx = determine_feedback_strategy("fake-id", "sh", 20)
        assert ctx.strategy == FeedbackStrategy.ADJUST

    @patch("apps.ai_tutor.feedback.get_attempts_for_phoneme", return_value=[])
    def test_strategy_always_valid(self, mock_attempts):
        valid_strategies = {FeedbackStrategy.ENCOURAGE, FeedbackStrategy.GUIDE, FeedbackStrategy.ADJUST}
        ctx = determine_feedback_strategy("fake-id", "sh", 50)
        assert ctx.strategy in valid_strategies
