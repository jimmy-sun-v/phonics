from django.shortcuts import redirect, render

from apps.games.models import Game
from apps.phonics.models import Phoneme, PhonemeCategory
from apps.phonics.services import get_all_categories, get_phoneme_detail, get_phonemes_by_category
from apps.sessions.services import create_session


def category_list_view(request):
    """Render the phonics category selection page."""
    categories = get_all_categories()

    category_meta = {
        "single_letter": {"icon": "🔤", "color": "#4CAF50"},
        "digraph": {"icon": "🔗", "color": "#2196F3"},
        "blend": {"icon": "🎨", "color": "#FF9800"},
        "long_vowel": {"icon": "📏", "color": "#9C27B0"},
        "r_controlled": {"icon": "🎯", "color": "#F44336"},
        "diphthong": {"icon": "🎵", "color": "#00BCD4"},
    }

    for cat in categories:
        meta = category_meta.get(cat["value"], {})
        cat["icon"] = meta.get("icon", "📖")
        cat["color"] = meta.get("color", "#666")

    return render(request, "phonics/categories.html", {"categories": categories})


def phoneme_list_view(request, category):
    """Render the phoneme list for a given category."""
    valid = [c[0] for c in PhonemeCategory.choices]
    if category not in valid:
        return redirect("phonics:category-list-page")

    phonemes = get_phonemes_by_category(category)
    category_label = dict(PhonemeCategory.choices).get(category, category)

    return render(request, "phonics/phoneme_list.html", {
        "phonemes": phonemes,
        "category": category,
        "category_label": category_label,
    })


def listen_step_view(request, symbol):
    phoneme = get_phoneme_detail(symbol)
    if phoneme is None:
        return redirect("phonics:category-list-page")

    session = create_session()
    request.session["learning_session_id"] = str(session.session_id)

    return render(request, "learning/listen.html", {"phoneme": phoneme})


def observe_step_view(request, symbol):
    phoneme = get_phoneme_detail(symbol)
    if phoneme is None:
        return redirect("phonics:category-list-page")

    example = phoneme.example_words[0] if phoneme.example_words else ""
    word_parts = _split_word_for_highlight(example, symbol)

    return render(request, "learning/observe.html", {
        "phoneme": phoneme,
        "word_parts": word_parts,
    })


def _split_word_for_highlight(word, phoneme_symbol):
    symbol = phoneme_symbol.replace("_", "")
    lower_word = word.lower()
    idx = lower_word.find(symbol.lower())

    if idx == -1:
        return [{"text": word, "highlight": False}]

    parts = []
    if idx > 0:
        parts.append({"text": word[:idx], "highlight": False})
    parts.append({"text": word[idx:idx + len(symbol)], "highlight": True})
    if idx + len(symbol) < len(word):
        parts.append({"text": word[idx + len(symbol):], "highlight": False})
    return parts


def repeat_step_view(request, symbol):
    phoneme = get_phoneme_detail(symbol)
    if phoneme is None:
        return redirect("phonics:category-list-page")

    session_id = request.session.get("learning_session_id", "")

    return render(request, "learning/repeat.html", {
        "phoneme": phoneme,
        "session_id": session_id,
    })


def practice_step_view(request, symbol):
    phoneme = get_phoneme_detail(symbol)
    if phoneme is None:
        return redirect("phonics:category-list-page")

    games = Game.objects.filter(is_active=True, phonemes=phoneme)
    return render(request, "learning/practice.html", {
        "phoneme": phoneme,
        "games": games,
    })


def reinforce_step_view(request, symbol):
    phoneme = get_phoneme_detail(symbol)
    if phoneme is None:
        return redirect("phonics:category-list-page")

    total_count = Phoneme.objects.filter(category=phoneme.category).count()
    current_order = phoneme.display_order
    completed_count = Phoneme.objects.filter(
        category=phoneme.category,
        display_order__lte=current_order,
    ).count()
    completion_pct = int((completed_count / total_count) * 100) if total_count > 0 else 0

    next_phoneme = Phoneme.objects.filter(
        category=phoneme.category,
        display_order__gt=phoneme.display_order,
    ).order_by("display_order").first()

    return render(request, "learning/reinforce.html", {
        "phoneme": phoneme,
        "completed_count": completed_count,
        "total_count": total_count,
        "completion_pct": completion_pct,
        "next_phoneme": next_phoneme,
    })
