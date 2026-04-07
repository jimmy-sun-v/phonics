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
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Show how many sessions would be purged without deleting them",
        )

    def handle(self, *args, **options):
        hours = options["hours"]
        dry_run = options["dry_run"]

        if dry_run:
            from datetime import timedelta

            from django.conf import settings
            from django.utils import timezone

            from apps.sessions.models import LearningSession

            retention = hours if hours is not None else getattr(settings, "SESSION_RETENTION_HOURS", 24)
            threshold = timezone.now() - timedelta(hours=retention)
            count = LearningSession.objects.filter(last_active_at__lt=threshold).count()
            self.stdout.write(f"Dry run: would purge {count} expired session(s)")
        else:
            count = purge_expired_sessions(retention_hours=hours)
            self.stdout.write(self.style.SUCCESS(f"Purged {count} expired session(s)"))
