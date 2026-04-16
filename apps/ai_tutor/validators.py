import logging
import random
import re

logger = logging.getLogger(__name__)

FALLBACK_MESSAGES = [
    "Great try! Let's practice that sound again!",
    "You're doing awesome! Let's try one more time!",
    "Nice effort! Let's keep going!",
]

FORBIDDEN_WORDS = [
    "wrong",
    "incorrect",
    "mistake",
    "fail",
    "bad",
    "stupid",
    "dumb",
    "no",
    "can't",
]

PERSONAL_QUESTION_PATTERNS = [
    r"\bwhat(?:'s| is) your name\b",
    r"\bhow old are you\b",
    r"\bwhere do you live\b",
    r"\bwhat(?:'s| is) your (?:age|school|address|phone)\b",
    r"\btell me about (?:your|you)\b",
]

MAX_SENTENCES = 2
MAX_WORDS = 10


def validate_response(response_text: str) -> str:
    if not response_text or not response_text.strip():
        logger.warning("Empty LLM response, using fallback")
        return _get_fallback()

    text = response_text.strip()

    text_lower = text.lower()
    for word in FORBIDDEN_WORDS:
        if re.search(rf"\b{re.escape(word)}\b", text_lower):
            logger.warning("Forbidden word '%s' detected in LLM response, using fallback", word)
            return _get_fallback()

    for pattern in PERSONAL_QUESTION_PATTERNS:
        if re.search(pattern, text_lower):
            logger.warning("Personal question detected in LLM response, using fallback")
            return _get_fallback()

    sentences = _split_sentences(text)
    if len(sentences) > MAX_SENTENCES:
        logger.info("LLM response too long (%d sentences), truncating to %d", len(sentences), MAX_SENTENCES)
        text = " ".join(sentences[:MAX_SENTENCES])

    words = text.split()
    if len(words) > MAX_WORDS:
        logger.info("LLM response too long (%d words), truncating to %d", len(words), MAX_WORDS)
        text = " ".join(words[:MAX_WORDS]).rstrip(",.;:")
        if not text.endswith((".", "!", "?")):
            text += "!"

    return text


def _split_sentences(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if s.strip()]


def _get_fallback() -> str:
    return random.choice(FALLBACK_MESSAGES)
