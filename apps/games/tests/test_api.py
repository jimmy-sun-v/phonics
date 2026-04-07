import pytest
from rest_framework.test import APIClient

from apps.games.models import Game, GamePhonemeMapping, GameType
from apps.phonics.models import Phoneme


@pytest.mark.django_db
class TestGamesAPI:
    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def phoneme(self):
        p, _ = Phoneme.objects.get_or_create(symbol="zz", defaults={"category": "digraph"})
        return p

    @pytest.fixture
    def game(self, phoneme):
        game = Game.objects.create(name="Sound Match", game_type=GameType.SOUND_PICTURE, is_active=True)
        GamePhonemeMapping.objects.create(game=game, phoneme=phoneme)
        return game

    def test_list_active_games(self, client, game):
        Game.objects.create(name="Hidden", game_type=GameType.BALLOON_POP, is_active=False)
        response = client.get("/api/games/")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Sound Match"

    def test_game_detail_with_phonemes(self, client, game):
        response = client.get(f"/api/games/{game.pk}/")
        assert response.status_code == 200
        assert "zz" in response.data["phonemes"]

    def test_game_not_found(self, client):
        response = client.get("/api/games/99999/")
        assert response.status_code == 404

    def test_games_for_phoneme(self, client, game, phoneme):
        response = client.get("/api/games/for-phoneme/zz/")
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_games_for_unknown_phoneme(self, client):
        response = client.get("/api/games/for-phoneme/zzz/")
        assert response.status_code == 404
