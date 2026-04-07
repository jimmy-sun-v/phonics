from django.db import models


class PhonemeCategory(models.TextChoices):
    SINGLE_LETTER = "single_letter", "Single Letter Sound"
    DIGRAPH = "digraph", "Digraph"
    BLEND = "blend", "Blend"
    LONG_VOWEL = "long_vowel", "Long Vowel Pattern"
    R_CONTROLLED = "r_controlled", "R-Controlled Vowel"
    DIPHTHONG = "diphthong", "Diphthong"


class Phoneme(models.Model):
    symbol = models.CharField(
        max_length=10,
        unique=True,
        help_text="The phoneme symbol, e.g., 'sh', 'ch', 'a_e'",
    )
    category = models.CharField(
        max_length=20,
        choices=PhonemeCategory.choices,
        db_index=True,
        help_text="Phonics category this phoneme belongs to",
    )
    example_words = models.JSONField(
        default=list,
        help_text="List of example words containing this phoneme, e.g., ['ship', 'shop']",
    )
    audio_file = models.FileField(
        upload_to="phonics/audio/",
        blank=True,
        null=True,
        help_text="Optional pre-recorded audio file for this phoneme",
    )
    display_order = models.IntegerField(
        default=0,
        db_index=True,
        help_text="Order for display within a category (lower = first)",
    )

    class Meta:
        ordering = ["category", "display_order", "symbol"]
        verbose_name = "Phoneme"
        verbose_name_plural = "Phonemes"

    def __str__(self):
        return f"{self.symbol} ({self.get_category_display()})"
