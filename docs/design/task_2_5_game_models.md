# Design: Task 2.5 – Game & GamePhonemeMapping Models

## Overview

Define `Game` and `GamePhonemeMapping` models in the `games` app for game definitions and their associations with phonemes.

## Dependencies

- Task 2.1 (Phoneme model)

## Detailed Design

### Model Definitions

**File: `apps/games/models.py`**

```python
from django.db import models


class GameType(models.TextChoices):
    SOUND_PICTURE = "sound_picture", "Sound → Picture Matching"
    BEGINNING_SOUND = "beginning_sound", "Beginning Sound Selection"
    BLEND_BUILDER = "blend_builder", "Blend Builder"
    BALLOON_POP = "balloon_pop", "Balloon Pop"


class Game(models.Model):
    name = models.CharField(
        max_length=100,
        help_text="Display name of the game",
    )
    game_type = models.CharField(
        max_length=20,
        choices=GameType.choices,
        help_text="Type/mechanic of the game",
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the game for display",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this game is available for play",
    )
    phonemes = models.ManyToManyField(
        "phonics.Phoneme",
        through="GamePhonemeMapping",
        related_name="games",
        help_text="Phonemes this game supports",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Game"
        verbose_name_plural = "Games"

    def __str__(self):
        return f"{self.name} ({self.get_game_type_display()})"


class GamePhonemeMapping(models.Model):
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name="phoneme_mappings",
    )
    phoneme = models.ForeignKey(
        "phonics.Phoneme",
        on_delete=models.CASCADE,
        related_name="game_mappings",
    )

    class Meta:
        unique_together = [("game", "phoneme")]
        verbose_name = "Game-Phoneme Mapping"
        verbose_name_plural = "Game-Phoneme Mappings"

    def __str__(self):
        return f"{self.game.name} ↔ {self.phoneme.symbol}"
```

### Design Decisions

- **ManyToManyField with explicit through model**: Allows adding extra fields to the mapping later (e.g., difficulty, configuration) without migration headaches.
- **`unique_together`**: Prevents duplicate (game, phoneme) pairs at the database level.
- **4 game types**: Matches the App_Overview §3.3 specification exactly.
- **`is_active`**: Allows games to be disabled without deletion.

### Admin Registration

**File: `apps/games/admin.py`**

```python
from django.contrib import admin
from .models import Game, GamePhonemeMapping


class GamePhonemeMappingInline(admin.TabularInline):
    model = GamePhonemeMapping
    extra = 1


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("name", "game_type", "is_active")
    list_filter = ("game_type", "is_active")
    search_fields = ("name",)
    inlines = [GamePhonemeMappingInline]


@admin.register(GamePhonemeMapping)
class GamePhonemeMappingAdmin(admin.ModelAdmin):
    list_display = ("game", "phoneme")
    list_filter = ("game__game_type",)
```

### Database Schema

Table: `games_game`

| Column | Type | Constraints |
|--------|------|-------------|
| id | bigint | PK, auto-increment |
| name | varchar(100) | NOT NULL |
| game_type | varchar(20) | NOT NULL |
| description | text | NOT NULL (can be empty) |
| is_active | boolean | NOT NULL, default true, indexed |

Table: `games_gamephonememapping`

| Column | Type | Constraints |
|--------|------|-------------|
| id | bigint | PK, auto-increment |
| game_id | bigint | FK → games_game(id), CASCADE |
| phoneme_id | bigint | FK → phonics_phoneme(id), CASCADE |
| | | UNIQUE(game_id, phoneme_id) |

## Acceptance Criteria

- [ ] 4 game types defined as choices
- [ ] Game can be linked to multiple phonemes
- [ ] Phoneme can be linked to multiple games (M2M)
- [ ] Duplicate (game, phoneme) pairs raise `IntegrityError`
- [ ] Admin shows games with inline phoneme mappings

## Test Strategy

**File: `apps/games/tests/test_models.py`**

```python
import pytest
from django.db import IntegrityError
from apps.games.models import Game, GamePhonemeMapping, GameType
from apps.phonics.models import Phoneme


@pytest.mark.django_db
class TestGameModels:
    @pytest.fixture
    def phoneme(self):
        return Phoneme.objects.create(symbol="sh", category="digraph")

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
        game = Game.objects.create(name="Hidden", game_type=GameType.BALLOON_POP, is_active=False)
        assert Game.objects.filter(is_active=True).count() == 0
        assert Game.objects.filter(is_active=False).count() == 1
```
