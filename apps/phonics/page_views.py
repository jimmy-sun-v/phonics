from django.shortcuts import redirect, render

from apps.phonics.models import PhonemeCategory
from apps.phonics.services import get_all_categories, get_phonemes_by_category


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
