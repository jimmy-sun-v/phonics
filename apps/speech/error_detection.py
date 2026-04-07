from dataclasses import dataclass

from django.conf import settings

SUBSTITUTION_MAP: dict[str, list[str]] = {
    "sh": ["s", "ch"],
    "ch": ["sh", "t"],
    "th": ["f", "d", "v"],
    "wh": ["w"],
    "ph": ["f"],
    "ng": ["n"],
    "kn": ["n"],
    "wr": ["r"],
    "bl": ["b"],
    "cl": ["c", "k"],
    "fl": ["f"],
    "gr": ["g"],
    "st": ["s", "t"],
    "tr": ["t", "ch"],
    "v": ["f", "b"],
    "b": ["p", "d"],
    "d": ["t", "b"],
    "g": ["k", "d"],
    "p": ["b"],
    "t": ["d"],
}


@dataclass
class ErrorDetectionResult:
    is_correct: bool
    confidence: float
    detected_error: str | None


def detect_error(expected_phoneme: str, stt_text: str, confidence: float) -> ErrorDetectionResult:
    low_confidence_threshold = getattr(settings, "LOW_CONFIDENCE_THRESHOLD", 0.5)

    stt_lower = stt_text.lower().strip()
    phoneme_lower = expected_phoneme.lower().strip()

    if confidence < low_confidence_threshold:
        detected = _find_substitution(phoneme_lower, stt_lower)
        return ErrorDetectionResult(is_correct=False, confidence=confidence, detected_error=detected)

    if _text_matches_phoneme(phoneme_lower, stt_lower):
        return ErrorDetectionResult(is_correct=True, confidence=confidence, detected_error=None)

    detected = _find_substitution(phoneme_lower, stt_lower)
    return ErrorDetectionResult(is_correct=False, confidence=confidence, detected_error=detected)


def _text_matches_phoneme(phoneme: str, text: str) -> bool:
    if not text:
        return False
    if text == phoneme:
        return True
    if text.startswith(phoneme):
        return True
    if "_" in phoneme:
        parts = phoneme.split("_")
        if len(parts) == 2:
            vowel, ending = parts
            if vowel in text and text.endswith(ending):
                return True
    return False


def _find_substitution(expected: str, text: str) -> str | None:
    if not text or expected not in SUBSTITUTION_MAP:
        return None
    for sub in SUBSTITUTION_MAP[expected]:
        if text.startswith(sub) and not text.startswith(expected):
            return f"/{sub}/"
    return None
