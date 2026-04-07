import uuid

from django.db import models


class LearningSession(models.Model):
    session_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Auto-generated anonymous session identifier",
    )
    current_phoneme = models.ForeignKey(
        "phonics.Phoneme",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="active_sessions",
        help_text="The phoneme the child is currently working on",
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the session was created",
    )
    last_active_at = models.DateTimeField(
        auto_now=True,
        help_text="Last activity timestamp (auto-updated on save)",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this session is still active",
    )

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Learning Session"
        verbose_name_plural = "Learning Sessions"

    def __str__(self):
        return f"Session {self.session_id} ({'active' if self.is_active else 'inactive'})"
