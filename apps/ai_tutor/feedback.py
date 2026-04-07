from dataclasses import dataclass, field

from apps.sessions.progress import get_attempts_for_phoneme


class FeedbackStrategy:
    ENCOURAGE = "encourage"
    GUIDE = "guide"
    ADJUST = "adjust"


@dataclass
class FeedbackContext:
    strategy: str
    hints: list[str] = field(default_factory=list)
    attempt_count: int = 0
    best_confidence: float = 0.0


def determine_feedback_strategy(
    session_id,
    phoneme_symbol: str,
    current_confidence: float,
) -> FeedbackContext:
    attempts = get_attempts_for_phoneme(session_id, phoneme_symbol)
    attempt_count = len(attempts)

    best_confidence = current_confidence
    if attempts:
        best_confidence = max(max(a.confidence for a in attempts), current_confidence)

    if attempt_count <= 1:
        if current_confidence >= 0.6:
            return FeedbackContext(
                strategy=FeedbackStrategy.ENCOURAGE,
                attempt_count=attempt_count,
                best_confidence=best_confidence,
            )
        else:
            return FeedbackContext(
                strategy=FeedbackStrategy.GUIDE,
                hints=_get_guide_hints(phoneme_symbol),
                attempt_count=attempt_count,
                best_confidence=best_confidence,
            )
    elif attempt_count == 2:
        return FeedbackContext(
            strategy=FeedbackStrategy.GUIDE,
            hints=_get_guide_hints(phoneme_symbol),
            attempt_count=attempt_count,
            best_confidence=best_confidence,
        )
    else:
        return FeedbackContext(
            strategy=FeedbackStrategy.ADJUST,
            hints=_get_adjust_hints(phoneme_symbol),
            attempt_count=attempt_count,
            best_confidence=best_confidence,
        )


def _get_guide_hints(phoneme_symbol: str) -> list[str]:
    hints_map = {
        "sh": ["Put your finger to your lips like saying 'shhh'"],
        "ch": ["It's like the sound a train makes: choo choo!"],
        "th": ["Gently put your tongue between your teeth and blow"],
        "bl": ["Start with 'b' and slide into 'l'"],
        "tr": ["Start with 't' and slide into 'r'"],
    }
    return hints_map.get(phoneme_symbol, ["Listen carefully and try again"])


def _get_adjust_hints(phoneme_symbol: str) -> list[str]:
    base_hints = _get_guide_hints(phoneme_symbol)
    return base_hints + ["Let's listen to the sound one more time", "Try saying it slowly"]
