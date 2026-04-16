import pytest

from apps.phonics.models import Phoneme
from apps.phonics.services import (
    get_all_categories,
    get_next_phoneme,
    get_phoneme_detail,
    get_phonemes_by_category,
)
from apps.sessions.models import LearningSession
from apps.speech.models import SpeechAttempt


@pytest.mark.django_db
class TestPhonicsService:
    def test_get_all_categories(self):
        categories = get_all_categories()
        assert len(categories) == 6
        names = [c["value"] for c in categories]
        assert "single_letter" in names
        assert "digraph" in names

    def test_get_phonemes_by_category(self):
        phonemes = get_phonemes_by_category("digraph")
        assert len(phonemes) == 8
        assert all(p.category == "digraph" for p in phonemes)

    def test_invalid_category_raises(self):
        with pytest.raises(ValueError):
            get_phonemes_by_category("invalid")

    def test_get_phoneme_detail(self):
        p = get_phoneme_detail("sh")
        assert p is not None
        assert p.symbol == "sh"

    def test_get_phoneme_detail_not_found(self):
        assert get_phoneme_detail("zzz") is None

    def test_get_next_phoneme_returns_first(self):
        session = LearningSession.objects.create()
        next_p = get_next_phoneme(session)
        assert next_p is not None
        assert next_p.category == "single_letter"

    def test_get_next_phoneme_skips_completed(self):
        session = LearningSession.objects.create()
        first = Phoneme.objects.filter(category="single_letter").order_by("display_order").first()
        SpeechAttempt.objects.create(session=session, phoneme=first, confidence=90, attempt_number=1)
        next_p = get_next_phoneme(session)
        assert next_p is not None
        assert next_p != first
