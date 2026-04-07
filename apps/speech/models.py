from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class SpeechAttempt(models.Model):
    session = models.ForeignKey(
        "learning_sessions.LearningSession",
        on_delete=models.CASCADE,
        related_name="speech_attempts",
        help_text="The learning session this attempt belongs to",
    )
    phoneme = models.ForeignKey(
        "phonics.Phoneme",
        on_delete=models.CASCADE,
        related_name="speech_attempts",
        help_text="The phoneme that was being practiced",
    )
    confidence = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Speech recognition confidence score (0.0-1.0)",
    )
    detected_error = models.CharField(  # noqa: DJ001
        max_length=50,
        blank=True,
        null=True,
        help_text="Detected substitution error, e.g., '/s/' for '/sh/'",
    )
    attempt_number = models.PositiveIntegerField(
        help_text="Sequential attempt number for this phoneme in this session",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this attempt was recorded",
    )

    class Meta:
        ordering = ["session", "phoneme", "attempt_number"]
        verbose_name = "Speech Attempt"
        verbose_name_plural = "Speech Attempts"
        indexes = [
            models.Index(fields=["session", "phoneme"], name="idx_attempt_session_phoneme"),
        ]

    def __str__(self):
        return f"Attempt {self.attempt_number}: {self.phoneme.symbol} (conf={self.confidence:.2f})"
