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
        self.stdout.write(self.style.SUCCESS(f"Purged {count} expired session(s)"))
