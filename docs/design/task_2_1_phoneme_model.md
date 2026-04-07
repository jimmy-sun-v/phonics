# Design: Task 2.1 – Phoneme Model & Migration

## Overview

Define the `Phoneme` model in the `phonics` app with all required fields, create the migration, and register in Django admin.

## Dependencies

- Task 1.2 (phonics app skeleton)
- Task 1.8 (database connection)

## Detailed Design

### Model Definition

**File: `apps/phonics/models.py`**

```python
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
```

### Field Rationale

| Field | Type | Why |
|-------|------|-----|
| `symbol` | CharField(10), unique | Short strings like "sh", "a_e", "oi". Unique constraint prevents duplicates. |
| `category` | CharField(20) with choices | TextChoices enum enforces valid categories at model & form level. |
| `example_words` | JSONField | Flexible list storage. No need for a separate Word model at this stage. |
| `audio_file` | FileField, optional | Pre-recorded audio is optional; TTS can generate audio on-the-fly. |
| `display_order` | IntegerField | Controls ordering within a category. Indexed for efficient sorting. |

### Admin Registration

**File: `apps/phonics/admin.py`**

```python
from django.contrib import admin
from .models import Phoneme


@admin.register(Phoneme)
class PhonemeAdmin(admin.ModelAdmin):
    list_display = ("symbol", "category", "display_order")
    list_filter = ("category",)
    search_fields = ("symbol",)
    ordering = ("category", "display_order")
    list_editable = ("display_order",)
```

### Migration

Run after creating the model:
```powershell
python manage.py makemigrations phonics
python manage.py migrate
```

This generates `apps/phonics/migrations/0001_initial.py` with the `Phoneme` table.

### Database Schema

Table: `phonics_phoneme`

| Column | Type | Constraints |
|--------|------|-------------|
| id | bigint | PK, auto-increment |
| symbol | varchar(10) | UNIQUE, NOT NULL |
| category | varchar(20) | NOT NULL, indexed |
| example_words | jsonb (PostgreSQL) / text (SQLite) | NOT NULL, default [] |
| audio_file | varchar(100) | NULL |
| display_order | integer | NOT NULL, default 0, indexed |

## Acceptance Criteria

- [ ] Migration generated and applied cleanly
- [ ] `Phoneme.objects.create(symbol="sh", category="digraph", example_words=["ship","shop"])` succeeds
- [ ] Admin interface shows Phoneme list with filter by category
- [ ] Invalid category value raises ValidationError
- [ ] Symbol uniqueness enforced at DB level

## Test Strategy

**File: `apps/phonics/tests/test_models.py`**

```python
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from apps.phonics.models import Phoneme, PhonemeCategory


@pytest.mark.django_db
class TestPhonemeModel:
    def test_create_phoneme(self):
        p = Phoneme.objects.create(
            symbol="sh",
            category=PhonemeCategory.DIGRAPH,
            example_words=["ship", "shop"],
            display_order=1,
        )
        assert p.pk is not None
        assert p.symbol == "sh"
        assert p.category == "digraph"

    def test_unique_symbol(self):
        Phoneme.objects.create(symbol="sh", category=PhonemeCategory.DIGRAPH)
        with pytest.raises(IntegrityError):
            Phoneme.objects.create(symbol="sh", category=PhonemeCategory.DIGRAPH)

    def test_invalid_category_rejected(self):
        p = Phoneme(symbol="xx", category="invalid_category")
        with pytest.raises(ValidationError):
            p.full_clean()

    def test_default_ordering(self):
        Phoneme.objects.create(symbol="ch", category=PhonemeCategory.DIGRAPH, display_order=2)
        Phoneme.objects.create(symbol="sh", category=PhonemeCategory.DIGRAPH, display_order=1)
        phonemes = list(Phoneme.objects.filter(category=PhonemeCategory.DIGRAPH))
        assert phonemes[0].symbol == "sh"
        assert phonemes[1].symbol == "ch"

    def test_str_representation(self):
        p = Phoneme(symbol="sh", category=PhonemeCategory.DIGRAPH)
        assert str(p) == "sh (Digraph)"

    def test_example_words_default_empty_list(self):
        p = Phoneme.objects.create(symbol="th", category=PhonemeCategory.DIGRAPH)
        assert p.example_words == []
```
