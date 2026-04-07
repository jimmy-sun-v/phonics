from apps.ai_tutor.validators import FALLBACK_MESSAGES, validate_response


class TestResponseValidator:
    def test_clean_response_passes(self):
        text = "Great job! The 'sh' sound is like a whisper."
        assert validate_response(text) == text

    def test_wrong_word_triggers_fallback(self):
        result = validate_response("That was wrong. Try again.")
        assert result in FALLBACK_MESSAGES

    def test_incorrect_word_triggers_fallback(self):
        result = validate_response("That's incorrect, try again.")
        assert result in FALLBACK_MESSAGES

    def test_negative_word_bad_triggers_fallback(self):
        result = validate_response("That was a bad attempt.")
        assert result in FALLBACK_MESSAGES

    def test_personal_question_triggers_fallback(self):
        result = validate_response("What's your name? Let's practice!")
        assert result in FALLBACK_MESSAGES

    def test_how_old_triggers_fallback(self):
        result = validate_response("How old are you? Great sound!")
        assert result in FALLBACK_MESSAGES

    def test_long_response_truncated(self):
        text = "Great try! Keep it up! You're almost there! One more time!"
        result = validate_response(text)
        assert len(result) < len(text)

    def test_empty_response_fallback(self):
        result = validate_response("")
        assert result in FALLBACK_MESSAGES

    def test_none_response_fallback(self):
        result = validate_response(None)
        assert result in FALLBACK_MESSAGES

    def test_whitespace_only_fallback(self):
        result = validate_response("   ")
        assert result in FALLBACK_MESSAGES

    def test_single_sentence_passes(self):
        text = "Wonderful! You made the 'sh' sound perfectly!"
        assert validate_response(text) == text

    def test_two_sentences_passes(self):
        text = "Great try! Let's practice again."
        assert validate_response(text) == text
