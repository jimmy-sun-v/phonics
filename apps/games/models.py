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
