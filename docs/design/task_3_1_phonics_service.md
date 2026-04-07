# Design: Task 3.1 – Phonics Engine Service

## Overview

Create a service layer in the `phonics` app that provides data access methods for phoneme categories, phonemes, and learning sequence logic.

## Dependencies

- Task 2.1 (Phoneme model)
- Task 2.2 (Seed data)

## Detailed Design

### Service Module

**File: `apps/phonics/services.py`**

```python
from apps.phonics.models import Phoneme, PhonemeCategory


def get_all_categories() -> list[dict]:
    """Return all phoneme categories with their display names.

    Returns:
        List of dicts: [{"value": "single_letter", "label": "Single Letter Sound", "count": 24}, ...]
    """
    categories = []
    for choice in PhonemeCategory.choices:
        count = Phoneme.objects.filter(category=choice[0]).count()
        categories.append({
            "value": choice[0],
            "label": choice[1],
            "count": count,
        })
    return categories


def get_phonemes_by_category(category: str) -> list[Phoneme]:
    """Return all phonemes for a given category, ordered by display_order.

    Args:
        category: One of PhonemeCategory values (e.g., "digraph")

    Returns:
        QuerySet of Phoneme objects ordered by display_order.

    Raises:
        ValueError: If category is not a valid PhonemeCategory value.
    """
    valid_categories = [c[0] for c in PhonemeCategory.choices]
    if category not in valid_categories:
        raise ValueError(f"Invalid category: {category}. Must be one of {valid_categories}")
    return list(Phoneme.objects.filter(category=category).order_by("display_order"))


def get_phoneme_detail(symbol: str) -> Phoneme | None:
    """Return a single phoneme by its symbol.

    Args:
        symbol: The phoneme symbol (e.g., "sh", "a_e")

    Returns:
        Phoneme instance or None if not found.
    """
    try:
        return Phoneme.objects.get(symbol=symbol)
    except Phoneme.DoesNotExist:
        return None


def get_next_phoneme(session) -> Phoneme | None:
    """Return the next phoneme in the learning sequence for a session.

    Logic:
    1. Get the current phoneme's category
    2. Find phonemes in the same category not yet completed (confidence >= threshold)
    3. If all in category done, move to next category
    4. If all categories done, return None

    Args:
        session: LearningSession instance

    Returns:
        Next Phoneme to practice, or None if all completed.
    """
    from apps.speech.models import SpeechAttempt
    from django.conf import settings

    confidence_threshold = getattr(settings, "PHONEME_COMPLETION_THRESHOLD", 0.7)

    # Get completed phoneme IDs for this session
    completed_phoneme_ids = set(
        SpeechAttempt.objects.filter(
            session=session,
            confidence__gte=confidence_threshold,
        ).values_list("phoneme_id", flat=True).distinct()
    )

    # Iterate through categories in order
    for category_value, _ in PhonemeCategory.choices:
        remaining = (
            Phoneme.objects
            .filter(category=category_value)
            .exclude(id__in=completed_phoneme_ids)
            .order_by("display_order")
        )
        if remaining.exists():
            return remaining.first()

    return None  # All phonemes completed
```

### Configuration

Add to `config/settings/base.py`:
```python
PHONEME_COMPLETION_THRESHOLD = 0.7  # Confidence threshold to consider a phoneme "completed"
```

### Key Design Decisions

1. **Service functions, not class**: Simple stateless functions are cleaner for this use case.
2. **`get_next_phoneme` logic**: Iterates categories in the order defined by `PhonemeCategory.choices`, which follows the pedagogical progression (single letters → digraphs → blends → etc.).
3. **Completion threshold**: Configurable via settings. A phoneme is "completed" when any attempt achieves confidence ≥ 0.7.
4. **Lazy import**: `SpeechAttempt` imported inside `get_next_phoneme` to avoid circular imports between apps.

## Acceptance Criteria

- [ ] `get_all_categories()` returns 6 categories with counts
- [ ] `get_phonemes_by_category("digraph")` returns correct phonemes in display_order
- [ ] `get_phoneme_detail("sh")` returns the "sh" Phoneme
- [ ] `get_phoneme_detail("nonexistent")` returns None
- [ ] `get_next_phoneme(session)` skips completed phonemes
- [ ] Invalid category raises ValueError

## Test Strategy

**File: `apps/phonics/tests/test_services.py`**

```python
import pytest
from apps.phonics.models import Phoneme, PhonemeCategory
from apps.phonics.services import (
    get_all_categories,
    get_phonemes_by_category,
    get_phoneme_detail,
    get_next_phoneme,
)
from apps.sessions.models import LearningSession
from apps.speech.models import SpeechAttempt


@pytest.mark.django_db
class TestPhonicsService:
    def test_get_all_categories(self):
        categories = get_all_categories()
        assert len(categories) == 6
        values = {c["value"] for c in categories}
        assert values == {"single_letter", "digraph", "blend", "long_vowel", "r_controlled", "diphthong"}

    def test_get_phonemes_by_category_ordered(self):
        phonemes = get_phonemes_by_category("digraph")
        assert len(phonemes) == 8
        # Verify ordering
        orders = [p.display_order for p in phonemes]
        assert orders == sorted(orders)

    def test_get_phonemes_invalid_category(self):
        with pytest.raises(ValueError):
            get_phonemes_by_category("invalid")

    def test_get_phoneme_detail_found(self):
        p = get_phoneme_detail("sh")
        assert p is not None
        assert p.symbol == "sh"

    def test_get_phoneme_detail_not_found(self):
        assert get_phoneme_detail("zzzz") is None

    def test_get_next_phoneme_skips_completed(self):
        session = LearningSession.objects.create()
        first = Phoneme.objects.filter(category="single_letter").order_by("display_order").first()
        # Mark first phoneme as completed
        SpeechAttempt.objects.create(
            session=session, phoneme=first, confidence=0.9, attempt_number=1
        )
        next_p = get_next_phoneme(session)
        assert next_p != first
        assert next_p is not None
```
