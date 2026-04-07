from apps.speech.error_detection import detect_error


class TestErrorDetection:
    def test_exact_match(self):
        result = detect_error("sh", "sh", 0.9)
        assert result.is_correct is True
        assert result.detected_error is None

    def test_word_starting_with_phoneme(self):
        result = detect_error("sh", "ship", 0.85)
        assert result.is_correct is True

    def test_common_substitution_s_for_sh(self):
        result = detect_error("sh", "sip", 0.7)
        assert result.is_correct is False
        assert result.detected_error == "/s/"

    def test_th_fronting(self):
        result = detect_error("th", "fink", 0.75)
        assert result.is_correct is False
        assert result.detected_error == "/f/"

    def test_low_confidence_always_incorrect(self):
        result = detect_error("sh", "ship", 0.3)
        assert result.is_correct is False

    def test_magic_e_pattern(self):
        result = detect_error("a_e", "cake", 0.85)
        assert result.is_correct is True
