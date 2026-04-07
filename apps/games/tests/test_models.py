import pytest
from django.db import IntegrityError

from apps.games.models import Game, GamePhonemeMapping, GameType
from apps.phonics.models import Phoneme


@pytest.mark.django_db
class TestGameModels:
    @pytest.fixture
    def phoneme(self):
        return Phoneme.objects.create(symbol="zz", category="digraph")

    def test_create_all_game_types(self):
        for gt in GameType:
            game = Game.objects.create(name=f"Test {gt.label}", game_type=gt.value)
            assert game.pk is not None
        assert Game.objects.count() == 4

    def test_map_phoneme_to_game(self, phoneme):
        game = Game.objects.create(name="Sound Match", game_type=GameType.SOUND_PICTURE)
        GamePhonemeMapping.objects.create(game=game, phoneme=phoneme)
        assert phoneme in game.phonemes.all()
        assert game in phoneme.games.all()

    def test_duplicate_mapping_rejected(self, phoneme):
        game = Game.objects.create(name="Sound Match", game_type=GameType.SOUND_PICTURE)
        GamePhonemeMapping.objects.create(game=game, phoneme=phoneme)
        with pytest.raises(IntegrityError):
            GamePhonemeMapping.objects.create(game=game, phoneme=phoneme)

    def test_inactive_game(self):
        Game.objects.create(name="Hidden", game_type=GameType.BALLOON_POP, is_active=False)
        assert Game.objects.filter(is_active=True).count() == 0
        assert Game.objects.filter(is_active=False).count() == 1
