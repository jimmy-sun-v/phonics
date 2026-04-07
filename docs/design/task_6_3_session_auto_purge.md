# Design: Task 6.3 – Session Auto-Purge Configuration

## Overview

Configure the `purge_expired_sessions` management command with adjustable retention period, and set up scheduling via Django management command (for manual/cron use) or Django-Q/Celery if available.

## Dependencies

- Task 2.7 (Session expiry service)

## Detailed Design

### Management Command

**File: `apps/sessions/management/commands/purge_sessions.py`**

```python
from django.core.management.base import BaseCommand
from apps.sessions.services import purge_expired_sessions


class Command(BaseCommand):
    help = "Purge expired learning sessions older than the configured retention period."

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours",
            type=int,
            default=None,
            help="Override retention hours (default: from settings or 24h)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show count of sessions that would be purged without deleting.",
        )

    def handle(self, *args, **options):
        hours = options["hours"]
        dry_run = options["dry_run"]

        if dry_run:
            from django.utils import timezone
            from datetime import timedelta
            from apps.sessions.models import LearningSession

            retention = hours or 24
            cutoff = timezone.now() - timedelta(hours=retention)
            count = LearningSession.objects.filter(
                is_active=False,
                updated_at__lt=cutoff,
            ).count()
            self.stdout.write(f"Would purge {count} expired sessions (>{retention}h old)")
            return

        deleted = purge_expired_sessions(retention_hours=hours)
        self.stdout.write(self.style.SUCCESS(f"Purged {deleted} expired sessions."))
```

### Configuration

**File: `config/settings/base.py`** (add)

```python
# Session auto-purge configuration
SESSION_RETENTION_HOURS = int(env("SESSION_RETENTION_HOURS", default=24))
```

**File: `.env.example`** (add)

```
SESSION_RETENTION_HOURS=24
```

### Update purge_expired_sessions service

```python
# apps/sessions/services.py (update)
from django.conf import settings

def purge_expired_sessions(retention_hours: int | None = None) -> int:
    cutoff = timezone.now() - timedelta(
        hours=retention_hours or settings.SESSION_RETENTION_HOURS
    )
    result = LearningSession.objects.filter(
        is_active=False,
        updated_at__lt=cutoff,
    ).delete()
    return result[0]
```

### Cron Scheduling

For Azure App Service, use a WebJob or Azure Functions timer trigger.

For local/dev, use system cron:
```bash
# Run daily at 3 AM
0 3 * * * cd /path/to/project && python manage.py purge_sessions
```

## Acceptance Criteria

- [ ] `python manage.py purge_sessions` deletes expired sessions
- [ ] `--hours 48` overrides retention period
- [ ] `--dry-run` shows count without deleting
- [ ] Retention configurable via `SESSION_RETENTION_HOURS` env var
- [ ] Default retention: 24 hours

## Test Strategy

```python
# tests/test_purge_command.py
import pytest
from django.core.management import call_command
from io import StringIO
from datetime import timedelta
from django.utils import timezone


@pytest.mark.django_db
class TestPurgeCommand:
    def test_purge_deletes_old_sessions(self, learning_session_factory):
        old = learning_session_factory.create(
            is_active=False,
            updated_at=timezone.now() - timedelta(hours=48),
        )
        recent = learning_session_factory.create(is_active=False)

        out = StringIO()
        call_command("purge_sessions", "--hours=24", stdout=out)
        assert "Purged 1" in out.getvalue()

    def test_dry_run(self, learning_session_factory):
        learning_session_factory.create(
            is_active=False,
            updated_at=timezone.now() - timedelta(hours=48),
        )

        out = StringIO()
        call_command("purge_sessions", "--dry-run", "--hours=24", stdout=out)
        assert "Would purge 1" in out.getvalue()
```
