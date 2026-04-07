import pytest

from apps.phonics.models import Phoneme, PhonemeCategory


@pytest.mark.django_db
class TestPhonemeSeedData:
    def test_total_phoneme_count(self):
        assert Phoneme.objects.count() == 59

    def test_single_letter_count(self):
        assert Phoneme.objects.filter(category=PhonemeCategory.SINGLE_LETTER).count() == 24

    def test_digraph_count(self):
        assert Phoneme.objects.filter(category=PhonemeCategory.DIGRAPH).count() == 8

    def test_blend_count(self):
        assert Phoneme.objects.filter(category=PhonemeCategory.BLEND).count() == 9

    def test_long_vowel_count(self):
        assert Phoneme.objects.filter(category=PhonemeCategory.LONG_VOWEL).count() == 9

    def test_r_controlled_count(self):
        assert Phoneme.objects.filter(category=PhonemeCategory.R_CONTROLLED).count() == 5

    def test_diphthong_count(self):
        assert Phoneme.objects.filter(category=PhonemeCategory.DIPHTHONG).count() == 4

    def test_specific_phonemes_exist(self):
        for symbol in ["sh", "ch", "a_e", "ar", "oi"]:
            assert Phoneme.objects.filter(symbol=symbol).exists()

    def test_all_have_example_words(self):
        for p in Phoneme.objects.all():
            assert len(p.example_words) >= 2, f"{p.symbol} has < 2 example words"
