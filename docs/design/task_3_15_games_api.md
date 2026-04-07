# Design: Task 3.15 – Game REST API Endpoints

## Overview

Create API endpoints for listing games, game details with phoneme mappings, and finding games for a specific phoneme.

## Dependencies

- Task 2.5 (Game models)
- Task 3.1 (Phonics service)

## Detailed Design

### URL Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/games/` | List active games |
| GET | `/api/games/{id}/` | Game detail with mapped phonemes |
| GET | `/api/games/for-phoneme/{symbol}/` | Games available for a phoneme |

### Serializers

**File: `apps/games/serializers.py`**

```python
from rest_framework import serializers
from apps.games.models import Game


class GameListSerializer(serializers.ModelSerializer):
    game_type_display = serializers.CharField(source="get_game_type_display", read_only=True)

    class Meta:
        model = Game
        fields = ["id", "name", "game_type", "game_type_display", "description", "is_active"]
        read_only_fields = fields


class GameDetailSerializer(serializers.ModelSerializer):
    game_type_display = serializers.CharField(source="get_game_type_display", read_only=True)
    phonemes = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ["id", "name", "game_type", "game_type_display", "description", "is_active", "phonemes"]
        read_only_fields = fields

    def get_phonemes(self, obj):
        return list(obj.phonemes.values_list("symbol", flat=True))
```

### Views

**File: `apps/games/views.py`**

```python
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.games.models import Game
from apps.games.serializers import GameListSerializer, GameDetailSerializer
from apps.phonics.models import Phoneme


@api_view(["GET"])
def game_list(request):
    """List all active games."""
    games = Game.objects.filter(is_active=True)
    serializer = GameListSerializer(games, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def game_detail(request, pk):
    """Get game detail with mapped phonemes."""
    try:
        game = Game.objects.get(pk=pk)
    except Game.DoesNotExist:
        return Response(
            {"error": "Game not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    serializer = GameDetailSerializer(game)
    return Response(serializer.data)


@api_view(["GET"])
def games_for_phoneme(request, symbol):
    """Get all active games available for a specific phoneme."""
    try:
        phoneme = Phoneme.objects.get(symbol=symbol)
    except Phoneme.DoesNotExist:
        return Response(
            {"error": f"Phoneme '{symbol}' not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    games = Game.objects.filter(is_active=True, phonemes=phoneme)
    serializer = GameListSerializer(games, many=True)
    return Response(serializer.data)
```

### URLs

**File: `apps/games/urls.py`**

```python
from django.urls import path
from . import views

app_name = "games"

urlpatterns = [
    path("", views.game_list, name="game-list"),
    path("<int:pk>/", views.game_detail, name="game-detail"),
    path("for-phoneme/<str:symbol>/", views.games_for_phoneme, name="games-for-phoneme"),
]
```

### Sample Responses

**GET /api/games/**
```json
[
    {
        "id": 1,
        "name": "Sound Match",
        "game_type": "sound_picture",
        "game_type_display": "Sound → Picture Matching",
        "description": "Match the sound to the correct picture",
        "is_active": true
    }
]
```

**GET /api/games/1/**
```json
{
    "id": 1,
    "name": "Sound Match",
    "game_type": "sound_picture",
    "game_type_display": "Sound → Picture Matching",
    "description": "Match the sound to the correct picture",
    "is_active": true,
    "phonemes": ["sh", "ch", "th"]
}
```

## Acceptance Criteria

- [ ] List returns only active games
- [ ] Detail includes mapped phoneme symbols
- [ ] `for-phoneme/sh/` returns games mapped to "sh"
- [ ] Unknown game → 404
- [ ] Unknown phoneme → 404
- [ ] Inactive games excluded from list and for-phoneme

## Test Strategy

**File: `apps/games/tests/test_api.py`**

```python
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
        return Phoneme.objects.create(symbol="sh", category="digraph")

    @pytest.fixture
    def game(self, phoneme):
        game = Game.objects.create(
            name="Sound Match", game_type=GameType.SOUND_PICTURE, is_active=True
        )
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
        assert "sh" in response.data["phonemes"]

    def test_games_for_phoneme(self, client, game, phoneme):
        response = client.get("/api/games/for-phoneme/sh/")
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_games_for_unknown_phoneme(self, client):
        response = client.get("/api/games/for-phoneme/zz/")
        assert response.status_code == 404

    def test_game_not_found(self, client):
        response = client.get("/api/games/9999/")
        assert response.status_code == 404
```
