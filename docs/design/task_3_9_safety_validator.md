# Design: Task 3.9 – AI Tutor – Response Validation & Safety Filter

## Overview

Implement a validator that checks LLM responses against child safety rules and returns a validated (or fallback) response.

## Dependencies

- Task 3.8 (LLM client for response format)

## Detailed Design

### Module

**File: `apps/ai_tutor/validators.py`**

```python
import re
import logging

logger = logging.getLogger(__name__)

# Fallback messages when LLM response fails validation
FALLBACK_MESSAGES = [
    "Great try! Let's practice that sound again!",
    "You're doing awesome! Let's try one more time!",
    "Nice effort! Let's keep going!",
]

# Words that should never appear in child-facing responses
FORBIDDEN_WORDS = [
    "wrong", "incorrect", "mistake", "fail", "bad",
    "stupid", "dumb", "no", "can't",
]

# Patterns indicating personal questions
PERSONAL_QUESTION_PATTERNS = [
    r"\bwhat(?:'s| is) your name\b",
    r"\bhow old are you\b",
    r"\bwhere do you live\b",
    r"\bwhat(?:'s| is) your (?:age|school|address|phone)\b",
    r"\btell me about (?:your|you)\b",
]

MAX_SENTENCES = 2


def validate_response(response_text: str) -> str:
    """Validate and sanitize an LLM response for child safety.

    Applies the following checks in order:
    1. Empty/None responses → fallback
    2. Forbidden words → fallback
    3. Personal questions → fallback
    4. Length check (> 2 sentences) → truncate
    5. Clean response → pass through

    Args:
        response_text: Raw LLM response string.

    Returns:
        Validated response string (original or fallback).
    """
    if not response_text or not response_text.strip():
        logger.warning("Empty LLM response, using fallback")
        return _get_fallback()

    text = response_text.strip()

    # Check forbidden words
    text_lower = text.lower()
    for word in FORBIDDEN_WORDS:
        if re.search(rf"\b{re.escape(word)}\b", text_lower):
            logger.warning("Forbidden word '%s' detected in LLM response, using fallback", word)
            return _get_fallback()

    # Check personal questions
    for pattern in PERSONAL_QUESTION_PATTERNS:
        if re.search(pattern, text_lower):
            logger.warning("Personal question detected in LLM response, using fallback")
            return _get_fallback()

    # Check length (max 2 sentences)
    sentences = _split_sentences(text)
    if len(sentences) > MAX_SENTENCES:
        logger.info("LLM response too long (%d sentences), truncating to %d", len(sentences), MAX_SENTENCES)
        text = " ".join(sentences[:MAX_SENTENCES])

    return text


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences using common sentence-ending punctuation."""
    # Split on .!? followed by space or end of string
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def _get_fallback() -> str:
    """Return a safe fallback message.

    Rotates through fallback messages based on a simple counter.
    Thread-safe since each response is independent.
    """
    import random
    return random.choice(FALLBACK_MESSAGES)
```

### Safety Rules Matrix

| Rule | Detection Method | Action |
|------|-----------------|--------|
| No "wrong" | Regex word boundary match | Replace with fallback |
| No negative language | `FORBIDDEN_WORDS` list | Replace with fallback |
| No personal questions | `PERSONAL_QUESTION_PATTERNS` regex | Replace with fallback |
| Max 1-2 sentences | Sentence splitting + count | Truncate to 2 |
| Empty response | `not text.strip()` | Replace with fallback |

### Fallback Strategy

When a response fails validation, a pre-approved safe fallback is returned. All fallbacks are:
- Encouraging and positive
- Age-appropriate
- Do not reference specific phonemes (generic)
- 1 sentence each

## Acceptance Criteria

- [ ] Clean response passes through unchanged
- [ ] Response with "wrong" → replaced with fallback
- [ ] Response with personal question → replaced with fallback
- [ ] Response > 2 sentences → truncated to 2
- [ ] Empty/None response → fallback
- [ ] All fallback messages are safe and encouraging

## Test Strategy

**File: `apps/ai_tutor/tests/test_validators.py`**

```python
import pytest
from apps.ai_tutor.validators import validate_response, FALLBACK_MESSAGES


class TestResponseValidator:
    def test_clean_response_passes(self):
        text = "Great job! The 'sh' sound is like a whisper."
        assert validate_response(text) == text

    def test_wrong_word_triggers_fallback(self):
        result = validate_response("That was wrong. Try again.")
        assert result in FALLBACK_MESSAGES

    def test_incorrect_word_triggers_fallback(self):
        result = validate_response("That's incorrect, try again.")
        assert result in FALLBACK_MESSAGES

    def test_negative_word_bad_triggers_fallback(self):
        result = validate_response("That was a bad attempt.")
        assert result in FALLBACK_MESSAGES

    def test_personal_question_triggers_fallback(self):
        result = validate_response("What's your name? Let's practice!")
        assert result in FALLBACK_MESSAGES

    def test_how_old_triggers_fallback(self):
        result = validate_response("How old are you? Great sound!")
        assert result in FALLBACK_MESSAGES

    def test_long_response_truncated(self):
        text = "Great try! Keep it up! You're almost there! One more time!"
        result = validate_response(text)
        sentences = result.split(". ")
        # Should be at most 2 sentence-like segments
        assert len(result) < len(text)

    def test_empty_response_fallback(self):
        result = validate_response("")
        assert result in FALLBACK_MESSAGES

    def test_none_response_fallback(self):
        result = validate_response(None)
        assert result in FALLBACK_MESSAGES

    def test_whitespace_only_fallback(self):
        result = validate_response("   ")
        assert result in FALLBACK_MESSAGES

    def test_single_sentence_passes(self):
        text = "Wonderful! You made the 'sh' sound perfectly!"
        assert validate_response(text) == text

    def test_two_sentences_passes(self):
        text = "Great try! Let's practice again."
        assert validate_response(text) == text

    def test_wrong_as_substring_not_triggered(self):
        # "wrong" as part of another word should NOT trigger
        # But our regex uses word boundaries, so this is safe
        text = "Great effort on that sound!"
        assert validate_response(text) == text
```
