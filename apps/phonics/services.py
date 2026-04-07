from django.conf import settings

from apps.phonics.models import Phoneme, PhonemeCategory


def get_all_categories() -> list[dict]:
    categories = []
    for choice in PhonemeCategory.choices:
        count = Phoneme.objects.filter(category=choice[0]).count()
        categories.append(
            {
                "value": choice[0],
                "label": choice[1],
                "count": count,
            }
        )
    return categories


def get_phonemes_by_category(category: str) -> list[Phoneme]:
    valid_categories = [c[0] for c in PhonemeCategory.choices]
    if category not in valid_categories:
        raise ValueError(f"Invalid category: {category}. Must be one of {valid_categories}")
    return list(Phoneme.objects.filter(category=category).order_by("display_order"))


def get_phoneme_detail(symbol: str) -> Phoneme | None:
    try:
        return Phoneme.objects.get(symbol=symbol)
    except Phoneme.DoesNotExist:
        return None


def get_next_phoneme(session) -> Phoneme | None:
    from apps.speech.models import SpeechAttempt

    confidence_threshold = getattr(settings, "PHONEME_COMPLETION_THRESHOLD", 0.7)

    completed_phoneme_ids = set(
        SpeechAttempt.objects.filter(
            session=session,
            confidence__gte=confidence_threshold,
        )
        .values_list("phoneme_id", flat=True)
        .distinct()
    )

    for category_value, _ in PhonemeCategory.choices:
        remaining = (
            Phoneme.objects.filter(category=category_value)
            .exclude(id__in=completed_phoneme_ids)
            .order_by("display_order")
        )
        if remaining.exists():
            return remaining.first()

    return None
