import pytest
from apps.core.sanitize import sanitize_text_input, sanitize_phoneme_symbol


class TestSanitizeText:
    def test_strips_control_chars(self):
        assert sanitize_text_input("hello\x00world") == "helloworld"

    def test_truncates(self):
        assert len(sanitize_text_input("a" * 300)) == 200

    def test_strips_whitespace(self):
        assert sanitize_text_input("  hi  ") == "hi"

    def test_non_string(self):
        assert sanitize_text_input(None) == ""
        assert sanitize_text_input(123) == ""


class TestSanitizeSymbol:
    def test_valid_symbol(self):
        assert sanitize_phoneme_symbol("sh") == "sh"

    def test_rejects_special_chars(self):
        assert sanitize_phoneme_symbol("sh<script>") == "shscript"

    def test_lowercases(self):
        assert sanitize_phoneme_symbol("SH") == "sh"

    def test_allows_underscore(self):
        assert sanitize_phoneme_symbol("a_e") == "a_e"

    def test_non_string(self):
        assert sanitize_phoneme_symbol(None) == ""


@pytest.mark.django_db
class TestSecurityHeaders:
    def test_nosniff_header(self, client):
        resp = client.get("/phonics/")
        assert resp["X-Content-Type-Options"] == "nosniff"

    def test_frame_deny_header(self, client):
        resp = client.get("/phonics/")
        assert resp["X-Frame-Options"] == "DENY"

    def test_referrer_policy(self, client):
        resp = client.get("/phonics/")
        assert resp["Referrer-Policy"] == "strict-origin-when-cross-origin"
