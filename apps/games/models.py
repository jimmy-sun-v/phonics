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


class StorySession(models.Model):
    session = models.ForeignKey(
        "learning_sessions.LearningSession",
        on_delete=models.CASCADE,
        related_name="story_sessions",
        help_text="The learning session this story belongs to",
    )
    turns = models.JSONField(
        default=list,
        help_text='List of story turns: [{"role": "child"|"llm", "text": "..."}]',
    )
    max_rounds = models.PositiveIntegerField(
        default=4,
        help_text="Maximum number of child turns allowed",
    )
    is_complete = models.BooleanField(
        default=False,
        help_text="Whether the story has been completed",
    )
    summary = models.TextField(
        blank=True,
        help_text="LLM-generated summary of the completed story",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Story Session"
        verbose_name_plural = "Story Sessions"

    def __str__(self):
        return f"Story {self.pk} (session={self.session_id}, rounds={self.child_turn_count}/{self.max_rounds})"

    @property
    def child_turn_count(self):
        return sum(1 for t in self.turns if t.get("role") == "child")

    @property
    def round_number(self):
        return self.child_turn_count
