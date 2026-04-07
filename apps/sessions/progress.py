from django.conf import settings
from django.db.models import Max

from apps.phonics.models import Phoneme
from apps.sessions.models import LearningSession
from apps.speech.models import SpeechAttempt


def get_confidence_threshold() -> float:
    return getattr(settings, "PHONEME_COMPLETION_THRESHOLD", 0.7)


def record_attempt(
    session_id,
    phoneme_symbol: str,
    confidence: float,
    error: str | None = None,
) -> SpeechAttempt:
    session = LearningSession.objects.get(session_id=session_id)
    phoneme = Phoneme.objects.get(symbol=phoneme_symbol)

    max_attempt = SpeechAttempt.objects.filter(session=session, phoneme=phoneme).aggregate(
        max_num=Max("attempt_number")
    )
    next_number = (max_attempt["max_num"] or 0) + 1

    attempt = SpeechAttempt.objects.create(
        session=session,
        phoneme=phoneme,
        confidence=confidence,
        detected_error=error,
        attempt_number=next_number,
    )

    session.save()
    return attempt


def get_progress(session_id) -> dict:
    session = LearningSession.objects.get(session_id=session_id)
    threshold = get_confidence_threshold()

    all_phonemes = Phoneme.objects.all()
    attempts = SpeechAttempt.objects.filter(session=session)

    attempted_phonemes = {}
    for attempt in attempts.select_related("phoneme"):
        pid = attempt.phoneme_id
        if pid not in attempted_phonemes:
            attempted_phonemes[pid] = {
                "symbol": attempt.phoneme.symbol,
                "attempts": 0,
                "best_confidence": 0.0,
            }
        attempted_phonemes[pid]["attempts"] += 1
        attempted_phonemes[pid]["best_confidence"] = max(
            attempted_phonemes[pid]["best_confidence"],
            attempt.confidence,
        )

    completed = []
    in_progress = []
    remaining = []
    attempted_ids = set(attempted_phonemes.keys())

    for phoneme in all_phonemes:
        if phoneme.id in attempted_ids:
            data = attempted_phonemes[phoneme.id]
            if data["best_confidence"] >= threshold:
                completed.append({"symbol": data["symbol"], "best_confidence": data["best_confidence"]})
            else:
                in_progress.append(data)
        else:
            remaining.append({"symbol": phoneme.symbol})

    total = all_phonemes.count()
    completed_count = len(completed)

    return {
        "completed": completed,
        "in_progress": in_progress,
        "remaining": remaining,
        "total_phonemes": total,
        "completed_count": completed_count,
        "completion_percentage": round((completed_count / total) * 100, 1) if total > 0 else 0,
    }


def get_attempts_for_phoneme(session_id, phoneme_symbol: str) -> list[SpeechAttempt]:
    return list(
        SpeechAttempt.objects.filter(
            session_id=session_id,
            phoneme__symbol=phoneme_symbol,
        ).order_by("attempt_number")
    )
