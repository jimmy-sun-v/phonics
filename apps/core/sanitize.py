import re


def sanitize_text_input(text, max_length=200):
    if not isinstance(text, str):
        return ""
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = text.strip()
    return text[:max_length]


def sanitize_phoneme_symbol(symbol):
    if not isinstance(symbol, str):
        return ""
    cleaned = re.sub(r"[^a-z_]", "", symbol.lower())
    return cleaned[:10]
