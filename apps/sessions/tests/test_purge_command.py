import pytest
from io import StringIO
from datetime import timedelta

from django.core.management import call_command
from django.utils import timezone

from apps.sessions.models import LearningSession
from apps.phonics.models import Phoneme


@pytest.mark.django_db
class TestPurgeCommand:
    def _create_phoneme(self):
        return Phoneme.objects.create(
            symbol="zz",
            category="single_letter",
            example_words=["test"],
            display_order=999,
        )

    def test_purge_deletes_old_sessions(self):
        phoneme = self._create_phoneme()
        session = LearningSession.objects.create(current_phoneme=phoneme, is_active=False)
        LearningSession.objects.filter(pk=session.pk).update(
            last_active_at=timezone.now() - timedelta(hours=48)
        )

        out = StringIO()
        call_command("purge_expired_sessions", "--hours=24", stdout=out)
        output = out.getvalue()
        assert "1" in output
        assert LearningSession.objects.count() == 0

    def test_purge_keeps_recent_sessions(self):
        phoneme = self._create_phoneme()
        LearningSession.objects.create(current_phoneme=phoneme, is_active=False)

        out = StringIO()
        call_command("purge_expired_sessions", "--hours=24", stdout=out)
        assert LearningSession.objects.count() == 1

    def test_dry_run_does_not_delete(self):
        phoneme = self._create_phoneme()
        session = LearningSession.objects.create(current_phoneme=phoneme, is_active=False)
        LearningSession.objects.filter(pk=session.pk).update(
            last_active_at=timezone.now() - timedelta(hours=48)
        )

        out = StringIO()
        call_command("purge_expired_sessions", "--hours=24", "--dry-run", stdout=out)
        assert LearningSession.objects.count() == 1
        assert "dry run" in out.getvalue().lower() or "would purge" in out.getvalue().lower()
