from django.db import models


class PromptTemplate(models.Model):
    name = models.CharField(
        max_length=100,
        help_text="Identifier for this template, e.g., 'phonics_feedback'",
    )
    system_prompt = models.TextField(
        help_text="System-level prompt defining the AI tutor's behavior and constraints",
    )
    user_template = models.TextField(
        help_text="User message template with placeholders: {phoneme}, {confidence}, {error}, {attempts}",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this template is currently in use",
    )
    version = models.PositiveIntegerField(
        default=1,
        help_text="Version number for tracking template changes",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_active", "-version"]
        unique_together = [("name", "version")]
        verbose_name = "Prompt Template"
        verbose_name_plural = "Prompt Templates"

    def __str__(self):
        return f"{self.name} v{self.version} ({'active' if self.is_active else 'inactive'})"

    def render(self, phoneme: str, confidence: float, error: str | None, attempts: int) -> list[dict]:
        user_message = self.user_template.format(
            phoneme=phoneme,
            confidence=confidence,
            error=error or "none",
            attempts=attempts,
        )
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message},
        ]
