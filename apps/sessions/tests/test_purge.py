from datetime import timedelta

import pytest
from django.utils import timezone

from apps.phonics.models import Phoneme
from apps.sessions.models import LearningSession
from apps.sessions.services import purge_expired_sessions
from apps.speech.models import SpeechAttempt


@pytest.mark.django_db
class TestPurgeExpiredSessions:
    @pytest.fixture
    def phoneme(self):
        return Phoneme.objects.create(symbol="zz", category="digraph")

    def _create_old_session(self, hours_ago):
        session = LearningSession.objects.create()
        LearningSession.objects.filter(pk=session.pk).update(last_active_at=timezone.now() - timedelta(hours=hours_ago))
        return session

    def test_old_sessions_deleted(self):
        self._create_old_session(hours_ago=48)
        self._create_old_session(hours_ago=30)
        count = purge_expired_sessions(retention_hours=24)
        assert count == 2
        assert LearningSession.objects.count() == 0

    def test_recent_sessions_kept(self):
        LearningSession.objects.create()
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
        session = LearningSession.objects.get(pk=session.pk)
        SpeechAttempt.objects.create(session=session, phoneme=phoneme, confidence=50, attempt_number=1)
        purge_expired_sessions(retention_hours=24)
        assert SpeechAttempt.objects.count() == 0

    def test_configurable_threshold(self):
        self._create_old_session(hours_ago=8)
        count = purge_expired_sessions(retention_hours=6)
        assert count == 1
