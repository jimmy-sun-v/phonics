import random

from django.shortcuts import redirect, render

from apps.phonics.models import Phoneme
from apps.phonics.services import get_phoneme_detail

# Word-to-emoji mapping for the Sound Picture game.
# Covers first example words from phonemes.json.
WORD_EMOJI = {
    "bat": "🦇", "big": "🐘", "bus": "🚌",
    "cat": "🐱", "cup": "☕", "car": "🚗",
    "dog": "🐶", "dig": "⛏️", "day": "☀️",
    "fan": "🌀", "fun": "🎉", "fox": "🦊",
    "go": "🏃", "got": "✅", "gap": "🕳️",
    "hat": "🎩", "hen": "🐔", "hug": "🤗",
    "jam": "🍯", "jet": "✈️", "jog": "🏃",
    "kite": "🪁", "kid": "🧒", "key": "🔑",
    "lip": "👄", "log": "🪵", "let": "👋",
    "map": "🗺️", "mom": "👩", "mix": "🥣",
    "nap": "😴", "net": "🥅", "nut": "🥜",
    "pan": "🍳", "pet": "🐾", "pig": "🐷",
    "run": "🏃", "red": "🔴", "rat": "🐀",
    "sun": "☀️", "sit": "🪑", "sad": "😢",
    "top": "🔝", "ten": "🔟", "tap": "🚰",
    "van": "🚐", "vet": "👨\u200d⚕️", "vine": "🌿",
    "win": "🏆", "wet": "💧", "wag": "🐕",
    "yes": "👍", "yam": "🍠", "yell": "📢",
    "zip": "🤐", "zoo": "🦁", "zig": "⚡",
    "ant": "🐜", "apple": "🍎", "at": "📍",
    "egg": "🥚", "elf": "🧝", "end": "🔚",
    "it": "👆", "in": "📥", "igloo": "🏠",
    "on": "🔛", "ox": "🐂", "otter": "🦦",
    "up": "⬆️", "us": "👫", "umbrella": "☂️",
    "chip": "🍟", "chat": "💬", "chin": "😊",
    "ship": "🚢", "shop": "🛒", "shell": "🐚",
    "this": "👉", "that": "👈", "thin": "📏",
    "when": "⏰", "what": "❓", "whale": "🐋",
    "phone": "📱", "photo": "📸",
    "ring": "💍", "sing": "🎤", "king": "👑",
    "knee": "🦵", "knot": "🪢", "know": "🧠",
    "write": "✍️", "wrap": "🎁", "wren": "🐦",
    "blue": "🔵", "black": "⚫", "blend": "🫗",
    "clap": "👏", "clip": "📎", "clay": "🏺",
    "flag": "🚩", "fly": "🪰", "flip": "🔄",
    "green": "🟢", "grab": "🤲", "grin": "😁",
    "stop": "🛑", "star": "⭐", "step": "👣",
    "tree": "🌳", "trip": "🧳", "trap": "🪤",
    "jump": "🦘", "lamp": "💡", "camp": "⛺",
    "hand": "✋", "sand": "🏖️", "bend": "↩️",
    "pink": "💗", "tank": "🪖", "sink": "🚰",
    "cake": "🎂", "make": "🔨", "lake": "🏞️",
    "bike": "🚲", "like": "❤️",
    "bone": "🦴", "home": "🏠", "note": "🎵",
    "cute": "🥰", "mule": "🫏", "tube": "🧪",
    "rain": "🌧️", "tail": "🦊", "wait": "⏳",
    "bee": "🐝", "see": "👀",
    "boat": "⛵", "coat": "🧥", "road": "🛣️",
    "moon": "🌙", "food": "🍔", "pool": "🏊",
    "pie": "🥧", "tie": "👔", "lie": "🤥",
    "jar": "🫙",
    "her": "👩", "after": "➡️", "water": "💧",
    "bird": "🐦", "girl": "👧", "sir": "🎩",
    "for": "➡️", "horn": "📯", "corn": "🌽",
    "fur": "🧸", "burn": "🔥", "turn": "🔄",
    "oil": "🛢️", "coin": "🪙", "boil": "♨️",
    "boy": "👦", "toy": "🧸", "joy": "😊",
    "out": "👉", "cloud": "☁️", "house": "🏠",
    "cow": "🐄", "how": "❓", "now": "⏰",
}

DEFAULT_EMOJI = "🖼️"


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
                "emoji": WORD_EMOJI.get(phoneme.example_words[0], DEFAULT_EMOJI) if phoneme.example_words else DEFAULT_EMOJI,
                "is_correct": True}]

    for d in distractors:
        word = d.example_words[0] if d.example_words else d.symbol
        options.append({
            "word": word,
            "emoji": WORD_EMOJI.get(word, DEFAULT_EMOJI),
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
    example_emoji = WORD_EMOJI.get(example_word, DEFAULT_EMOJI)

    return render(request, "games/beginning_sound.html", {
        "phoneme": phoneme,
        "example_word": example_word,
        "example_emoji": example_emoji,
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
