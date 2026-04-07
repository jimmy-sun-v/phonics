import logging
from datetime import timedelta
from uuid import UUID

from django.conf import settings
from django.utils import timezone

from apps.phonics.models import Phoneme
from apps.sessions.models import LearningSession

logger = logging.getLogger(__name__)


class SessionNotFoundError(Exception):
    pass


class SessionInactiveError(Exception):
    pass


def create_session() -> LearningSession:
    session = LearningSession.objects.create()
    logger.info("Created new session: %s", session.session_id)
    return session


def get_session(session_id: UUID | str) -> LearningSession:
    try:
        return LearningSession.objects.get(session_id=session_id)
    except LearningSession.DoesNotExist:
        raise SessionNotFoundError(f"Session {session_id} not found") from None


def update_current_phoneme(session_id: UUID | str, phoneme_symbol: str) -> LearningSession:
    session = get_session(session_id)
    if not session.is_active:
        raise SessionInactiveError(f"Session {session_id} is inactive")
    phoneme = Phoneme.objects.get(symbol=phoneme_symbol)
    session.current_phoneme = phoneme
    session.save()
    return session


def deactivate_session(session_id: UUID | str) -> LearningSession:
    session = get_session(session_id)
    session.is_active = False
    session.save()
    logger.info("Deactivated session: %s", session.session_id)
    return session


def purge_expired_sessions(retention_hours: int | None = None) -> int:
    if retention_hours is None:
        retention_hours = getattr(settings, "SESSION_RETENTION_HOURS", 24)

    threshold = timezone.now() - timedelta(hours=retention_hours)
    expired = LearningSession.objects.filter(last_active_at__lt=threshold)
    count = expired.count()

    if count > 0:
        deleted_count, _ = expired.delete()
        logger.info(
            "Purged %d expired sessions (threshold: %d hours, cutoff: %s)",
            deleted_count,
            retention_hours,
            threshold.isoformat(),
        )
        return deleted_count

    logger.info("No expired sessions to purge (threshold: %d hours)", retention_hours)
    return 0
