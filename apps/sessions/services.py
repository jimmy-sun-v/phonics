import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.sessions.models import LearningSession

logger = logging.getLogger(__name__)


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
