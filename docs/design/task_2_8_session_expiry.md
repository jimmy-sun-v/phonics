# Design: Task 2.8 – Session Data Expiry Service

## Overview

Implement a service and management command to purge expired learning sessions and their related SpeechAttempt records, with a configurable retention period.

## Dependencies

- Task 2.3 (LearningSession model)
- Task 2.4 (SpeechAttempt model)

## Detailed Design

### Service Layer

**File: `apps/sessions/services.py`**

```python
import logging
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from apps.sessions.models import LearningSession

logger = logging.getLogger(__name__)


def purge_expired_sessions(retention_hours: int | None = None) -> int:
    """Delete learning sessions older than the retention threshold.

    SpeechAttempt records are cascade-deleted automatically via FK.

    Args:
        retention_hours: Override the default retention period.
            Defaults to settings.SESSION_RETENTION_HOURS (24).

    Returns:
        Number of sessions deleted.
    """
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
```

### Management Command

**File: `apps/sessions/management/__init__.py`** (empty)
**File: `apps/sessions/management/commands/__init__.py`** (empty)
**File: `apps/sessions/management/commands/purge_expired_sessions.py`**

```python
from django.core.management.base import BaseCommand
from apps.sessions.services import purge_expired_sessions


class Command(BaseCommand):
    help = "Purge learning sessions older than the configured retention period"

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours",
            type=int,
            default=None,
            help="Retention period in hours (default: SESSION_RETENTION_HOURS setting)",
        )

    def handle(self, *args, **options):
        hours = options["hours"]
        count = purge_expired_sessions(retention_hours=hours)
        self.stdout.write(
            self.style.SUCCESS(f"Purged {count} expired session(s)")
        )
```

### Usage

```powershell
# Use default retention (24 hours from settings)
python manage.py purge_expired_sessions

# Override with specific retention
python manage.py purge_expired_sessions --hours 12
```

### Cascade Behavior

When a `LearningSession` is deleted:
- All related `SpeechAttempt` records are cascade-deleted (defined by `on_delete=models.CASCADE` in Task 2.4)
- No orphaned speech attempts remain

### Configuration

In `config/settings/base.py` (from Task 1.7):
```python
SESSION_RETENTION_HOURS = env("SESSION_RETENTION_HOURS")  # default: 24
```

## Acceptance Criteria

- [ ] Sessions with `last_active_at` older than threshold are deleted
- [ ] Related SpeechAttempts are cascade-deleted
- [ ] Sessions within threshold are untouched
- [ ] Retention period configurable via `--hours` flag or `SESSION_RETENTION_HOURS` setting
- [ ] Command logs the count of deleted sessions

## Test Strategy

**File: `apps/sessions/tests/test_purge.py`**

```python
import pytest
from datetime import timedelta
from django.utils import timezone
from apps.sessions.models import LearningSession
from apps.speech.models import SpeechAttempt
from apps.phonics.models import Phoneme
from apps.sessions.services import purge_expired_sessions


@pytest.mark.django_db
class TestPurgeExpiredSessions:
    @pytest.fixture
    def phoneme(self):
        return Phoneme.objects.create(symbol="sh", category="digraph")

    def _create_old_session(self, hours_ago):
        session = LearningSession.objects.create()
        # Override the auto_now field directly in DB
        LearningSession.objects.filter(pk=session.pk).update(
            last_active_at=timezone.now() - timedelta(hours=hours_ago)
        )
        return session

    def test_old_sessions_deleted(self):
        self._create_old_session(hours_ago=48)
        self._create_old_session(hours_ago=30)
        count = purge_expired_sessions(retention_hours=24)
        assert count == 2
        assert LearningSession.objects.count() == 0

    def test_recent_sessions_kept(self):
        LearningSession.objects.create()  # just created = recent
        self._create_old_session(hours_ago=12)
        count = purge_expired_sessions(retention_hours=24)
        assert count == 0
        assert LearningSession.objects.count() == 2

    def test_mixed_old_and_new(self):
        LearningSession.objects.create()
        self._create_old_session(hours_ago=48)
        count = purge_expired_sessions(retention_hours=24)
        assert count == 1
        assert LearningSession.objects.count() == 1

    def test_cascade_deletes_attempts(self, phoneme):
        session = self._create_old_session(hours_ago=48)
        # Refresh to get actual session object
        session = LearningSession.objects.get(pk=session.pk)
        SpeechAttempt.objects.create(
            session=session, phoneme=phoneme, confidence=0.5, attempt_number=1
        )
        purge_expired_sessions(retention_hours=24)
        assert SpeechAttempt.objects.count() == 0

    def test_configurable_threshold(self):
        self._create_old_session(hours_ago=8)
        # With 6-hour retention, 8-hour-old session should be deleted
        count = purge_expired_sessions(retention_hours=6)
        assert count == 1
        # With 12-hour retention, same session age would survive
```
