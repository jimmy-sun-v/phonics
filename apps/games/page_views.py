import random

from django.shortcuts import redirect, render

from apps.phonics.models import Phoneme
from apps.phonics.services import get_phoneme_detail


def sound_picture_view(request, symbol):
    """Sound → Picture matching game."""
    phoneme = get_phoneme_detail(symbol)
    if phoneme is None:
        return redirect("phonics:category-list-page")

    # Build options: correct + 3 distractors from same category
    distractors = list(
        Phoneme.objects.filter(category=phoneme.category)
        .exclude(pk=phoneme.pk)
        .order_by("?")[:3]
    )

    options = [{"word": phoneme.example_words[0] if phoneme.example_words else phoneme.symbol,
                "image_path": f"images/phonemes/{phoneme.symbol}.png",
                "is_correct": True}]

    for d in distractors:
        options.append({
            "word": d.example_words[0] if d.example_words else d.symbol,
            "image_path": f"images/phonemes/{d.symbol}.png",
            "is_correct": False,
        })

    random.shuffle(options)

    return render(request, "games/sound_picture.html", {
        "phoneme": phoneme,
        "options": options,
    })


def beginning_sound_view(request, symbol):
    """Beginning Sound selection game."""
    phoneme = get_phoneme_detail(symbol)
    if phoneme is None:
        return redirect("phonics:category-list-page")

    distractors = list(
        Phoneme.objects.filter(category=phoneme.category)
        .exclude(pk=phoneme.pk)
        .order_by("?")[:3]
    )

    letter_options = [{"symbol": phoneme.symbol, "is_correct": True}]
    for d in distractors:
        letter_options.append({"symbol": d.symbol, "is_correct": False})

    random.shuffle(letter_options)

    example_word = phoneme.example_words[0] if phoneme.example_words else phoneme.symbol

    return render(request, "games/beginning_sound.html", {
        "phoneme": phoneme,
        "example_word": example_word,
        "letter_options": letter_options,
    })


def blend_builder_view(request, symbol):
    """Blend Builder drag & drop game."""
    phoneme = get_phoneme_detail(symbol)
    if phoneme is None:
        return redirect("phonics:category-list-page")

    target_word = phoneme.example_words[0] if phoneme.example_words else phoneme.symbol

    return render(request, "games/blend_builder.html", {
        "phoneme": phoneme,
        "target_word": target_word,
    })


def balloon_pop_view(request, symbol):
    """Balloon Pop game."""
    phoneme = get_phoneme_detail(symbol)
    if phoneme is None:
        return redirect("phonics:category-list-page")

    distractors = list(
        Phoneme.objects.filter(category=phoneme.category)
        .exclude(pk=phoneme.pk)
        .order_by("?")[:4]
        .values_list("symbol", flat=True)
    )

    return render(request, "games/balloon_pop.html", {
        "phoneme": phoneme,
        "distractors": distractors,
    })
