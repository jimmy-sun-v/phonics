# Design: Task 3.10 – Feedback Strategy Engine

## Overview

Implement logic that selects a feedback strategy based on attempt count and confidence history, providing metadata for prompt rendering.

## Dependencies

- Task 3.3 (Progress tracking for attempt history)
- Task 3.7 (Prompt rendering for consuming strategy metadata)

## Detailed Design

### Module

**File: `apps/ai_tutor/feedback.py`**

```python
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
    """Determine the appropriate feedback strategy based on attempt history.

    Strategy selection logic:
    - 1st attempt with confidence >= 0.6 → ENCOURAGE
    - 1st attempt with confidence < 0.6 → GUIDE
    - 2nd attempt → GUIDE (with specific hints)
    - 3+ attempts → ADJUST (simplified approach, more hints)

    Args:
        session_id: UUID of the session.
        phoneme_symbol: The phoneme being practiced.
        current_confidence: Confidence score from the current attempt.

    Returns:
        FeedbackContext with strategy type and optional hints.
    """
    attempts = get_attempts_for_phoneme(session_id, phoneme_symbol)
    attempt_count = len(attempts)

    # Calculate best confidence from history
    best_confidence = current_confidence
    if attempts:
        best_confidence = max(
            max(a.confidence for a in attempts),
            current_confidence,
        )

    # Strategy selection
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

    else:  # 3+ attempts
        return FeedbackContext(
            strategy=FeedbackStrategy.ADJUST,
            hints=_get_adjust_hints(phoneme_symbol),
            attempt_count=attempt_count,
            best_confidence=best_confidence,
        )


def _get_guide_hints(phoneme_symbol: str) -> list[str]:
    """Get simple guidance hints for the phoneme."""
    hints_map = {
        "sh": ["Put your finger to your lips like saying 'shhh'"],
        "ch": ["It's like the sound a train makes: choo choo!"],
        "th": ["Gently put your tongue between your teeth and blow"],
        "bl": ["Start with 'b' and slide into 'l'"],
        "tr": ["Start with 't' and slide into 'r'"],
    }
    return hints_map.get(phoneme_symbol, ["Listen carefully and try again"])


def _get_adjust_hints(phoneme_symbol: str) -> list[str]:
    """Get simplified hints for struggling learners."""
    base_hints = _get_guide_hints(phoneme_symbol)
    return base_hints + [
        "Let's listen to the sound one more time",
        "Try saying it slowly",
    ]
```

### Integration with Prompt Rendering

The `FeedbackContext` is used to enrich the prompt sent to the LLM. In the speech attempt orchestration (Task 3.13):

```python
feedback_ctx = determine_feedback_strategy(session_id, phoneme, confidence)
messages = render_prompt(
    phoneme=phoneme,
    confidence=confidence,
    error=detected_error,
    attempts=feedback_ctx.attempt_count,
)
# Strategy and hints can be appended to the user message or used to select a different template
```

### Strategy Selection Matrix

| Attempts | Confidence | Strategy | Behavior |
|----------|-----------|----------|----------|
| 1 | ≥ 0.6 | ENCOURAGE | Simple praise and move on |
| 1 | < 0.6 | GUIDE | Gentle guidance with hints |
| 2 | any | GUIDE | More specific guidance |
| 3+ | any | ADJUST | Simplified approach, extra hints |

## Acceptance Criteria

- [ ] 1st attempt, high confidence → "encourage"
- [ ] 1st attempt, low confidence → "guide" with hints
- [ ] 2nd attempt → "guide" with hints
- [ ] 3+ attempts → "adjust" with extended hints
- [ ] FeedbackContext always has valid strategy and attempt_count
- [ ] Hints are never discouraging

## Test Strategy

**File: `apps/ai_tutor/tests/test_feedback.py`**

```python
import pytest
from apps.ai_tutor.feedback import (
    determine_feedback_strategy,
    FeedbackStrategy,
)
from apps.sessions.models import LearningSession
from apps.speech.models import SpeechAttempt
from apps.phonics.models import Phoneme


@pytest.mark.django_db
class TestFeedbackStrategy:
    @pytest.fixture
    def session(self):
        return LearningSession.objects.create()

    @pytest.fixture
    def phoneme(self):
        return Phoneme.objects.create(symbol="sh", category="digraph", example_words=["ship"])

    def test_first_attempt_high_confidence_encourage(self, session, phoneme):
        ctx = determine_feedback_strategy(session.session_id, "sh", 0.85)
        assert ctx.strategy == FeedbackStrategy.ENCOURAGE
        assert ctx.attempt_count == 0  # No prior attempts

    def test_first_attempt_low_confidence_guide(self, session, phoneme):
        ctx = determine_feedback_strategy(session.session_id, "sh", 0.3)
        assert ctx.strategy == FeedbackStrategy.GUIDE
        assert len(ctx.hints) > 0

    def test_second_attempt_guide(self, session, phoneme):
        SpeechAttempt.objects.create(
            session=session, phoneme=phoneme, confidence=0.4, attempt_number=1
        )
        ctx = determine_feedback_strategy(session.session_id, "sh", 0.5)
        assert ctx.strategy == FeedbackStrategy.GUIDE

    def test_three_plus_attempts_adjust(self, session, phoneme):
        for i in range(1, 4):
            SpeechAttempt.objects.create(
                session=session, phoneme=phoneme, confidence=0.3, attempt_number=i
            )
        ctx = determine_feedback_strategy(session.session_id, "sh", 0.4)
        assert ctx.strategy == FeedbackStrategy.ADJUST
        assert "slowly" in " ".join(ctx.hints).lower() or "listen" in " ".join(ctx.hints).lower()

    def test_hints_never_discouraging(self, session, phoneme):
        for i in range(1, 6):
            SpeechAttempt.objects.create(
                session=session, phoneme=phoneme, confidence=0.2, attempt_number=i
            )
        ctx = determine_feedback_strategy(session.session_id, "sh", 0.2)
        all_hints = " ".join(ctx.hints).lower()
        assert "wrong" not in all_hints
        assert "bad" not in all_hints
        assert "fail" not in all_hints
```
