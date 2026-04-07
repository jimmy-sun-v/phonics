import pytest
from django.db import IntegrityError

from apps.phonics.models import Phoneme, PhonemeCategory


@pytest.mark.django_db
class TestPhonemeModel:
    def test_create_phoneme(self):
        p = Phoneme.objects.create(
            symbol="zz",
            category=PhonemeCategory.DIGRAPH,
            example_words=["fizz", "buzz"],
            display_order=99,
        )
        assert p.pk is not None
        assert p.symbol == "zz"
        assert p.category == "digraph"

    def test_unique_symbol(self):
        Phoneme.objects.create(symbol="xx", category=PhonemeCategory.DIGRAPH)
        with pytest.raises(IntegrityError):
            Phoneme.objects.create(symbol="xx", category=PhonemeCategory.DIGRAPH)

    def test_str_representation(self):
        p = Phoneme(symbol="yy", category=PhonemeCategory.DIGRAPH)
        assert str(p) == "yy (Digraph)"
