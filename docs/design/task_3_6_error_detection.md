# Design: Task 3.6 – Speech Error Detection Logic

## Overview

Implement logic to compare expected phoneme/word against actual STT transcription and detect common phoneme substitution errors.

## Dependencies

- Task 3.4 (STT service for result format)

## Detailed Design

### Module

**File: `apps/speech/error_detection.py`**

```python
from dataclasses import dataclass
from django.conf import settings


@dataclass
class ErrorDetectionResult:
    is_correct: bool
    confidence: float
    detected_error: str | None


# Common phoneme substitution pairs: {target: [common_substitutions]}
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


def detect_error(
    expected_phoneme: str,
    stt_text: str,
    confidence: float,
) -> ErrorDetectionResult:
    """Analyze STT result against expected phoneme to detect errors.

    Args:
        expected_phoneme: The phoneme symbol being practiced (e.g., "sh").
        stt_text: The text returned by STT (e.g., "ship" or "sip").
        confidence: STT confidence score (0.0–1.0).

    Returns:
        ErrorDetectionResult with correctness, confidence, and any detected error.
    """
    low_confidence_threshold = getattr(settings, "LOW_CONFIDENCE_THRESHOLD", 0.5)

    stt_lower = stt_text.lower().strip()
    phoneme_lower = expected_phoneme.lower().strip()

    # Case 1: Low confidence — flag regardless of text match
    if confidence < low_confidence_threshold:
        detected = _find_substitution(phoneme_lower, stt_lower)
        return ErrorDetectionResult(
            is_correct=False,
            confidence=confidence,
            detected_error=detected,
        )

    # Case 2: Check if the STT text contains the expected phoneme
    if _text_matches_phoneme(phoneme_lower, stt_lower):
        return ErrorDetectionResult(
            is_correct=True,
            confidence=confidence,
            detected_error=None,
        )

    # Case 3: No match — try to detect specific substitution
    detected = _find_substitution(phoneme_lower, stt_lower)
    return ErrorDetectionResult(
        is_correct=False,
        confidence=confidence,
        detected_error=detected,
    )


def _text_matches_phoneme(phoneme: str, text: str) -> bool:
    """Check if the recognized text contains the expected phoneme.

    For single phonemes (e.g., "sh"), checks if the text starts with
    or contains the phoneme sound appropriately.
    """
    if not text:
        return False

    # Direct match: text IS the phoneme
    if text == phoneme:
        return True

    # Text starts with the phoneme (e.g., "ship" starts with "sh")
    if text.startswith(phoneme):
        return True

    # For magic-e patterns like "a_e", check for the pattern in the word
    if "_" in phoneme:
        parts = phoneme.split("_")
        if len(parts) == 2:
            vowel, ending = parts
            # e.g., for "a_e": check "cake" contains "a" and ends with "e"
            if vowel in text and text.endswith(ending):
                return True

    return False


def _find_substitution(expected: str, text: str) -> str | None:
    """Check if the text suggests a common substitution error.

    Returns:
        The substituted phoneme string (e.g., "/s/") or None.
    """
    if not text or expected not in SUBSTITUTION_MAP:
        return None

    for sub in SUBSTITUTION_MAP[expected]:
        if text.startswith(sub) and not text.startswith(expected):
            return f"/{sub}/"

    return None
```

### Configuration

Add to `config/settings/base.py`:
```python
LOW_CONFIDENCE_THRESHOLD = 0.5  # Below this, always flag as incorrect
```

### Substitution Map Rationale

Common phoneme confusions for children aged 5–7:
- `/sh/` → `/s/`: "sip" instead of "ship" (fronting)
- `/th/` → `/f/`: "fink" instead of "think" (th-fronting)
- `/ch/` → `/sh/`: "shair" instead of "chair"
- `/tr/` → `/ch/`: "chee" instead of "tree" (affrication)

## Acceptance Criteria

- [ ] Exact match → `is_correct=True`
- [ ] Word starting with phoneme → `is_correct=True` (e.g., "ship" for "sh")
- [ ] Common substitution detected (e.g., `detected_error="/s/"` for expected "sh", got "sip")
- [ ] Low confidence → always `is_correct=False`
- [ ] Unknown substitution → `detected_error=None`

## Test Strategy

**File: `apps/speech/tests/test_error_detection.py`**

```python
import pytest
from apps.speech.error_detection import detect_error


class TestErrorDetection:
    def test_exact_match(self):
        result = detect_error("sh", "sh", 0.9)
        assert result.is_correct is True
        assert result.detected_error is None

    def test_word_starting_with_phoneme(self):
        result = detect_error("sh", "ship", 0.85)
        assert result.is_correct is True

    def test_common_substitution_s_for_sh(self):
        result = detect_error("sh", "sip", 0.7)
        assert result.is_correct is False
        assert result.detected_error == "/s/"

    def test_th_fronting(self):
        result = detect_error("th", "fink", 0.75)
        assert result.is_correct is False
        assert result.detected_error == "/f/"

    def test_low_confidence_always_incorrect(self):
        result = detect_error("sh", "ship", 0.3)
        assert result.is_correct is False

    def test_no_text_recognized(self):
        result = detect_error("sh", "", 0.0)
        assert result.is_correct is False

    def test_magic_e_pattern(self):
        result = detect_error("a_e", "cake", 0.85)
        assert result.is_correct is True

    def test_unknown_substitution(self):
        result = detect_error("sh", "banana", 0.8)
        assert result.is_correct is False
        assert result.detected_error is None
```
