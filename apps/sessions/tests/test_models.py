from uuid import UUID

import pytest

from apps.phonics.models import Phoneme
from apps.sessions.models import LearningSession


@pytest.mark.django_db
class TestLearningSessionModel:
    def test_create_session_auto_uuid(self):
        session = LearningSession.objects.create()
        assert isinstance(session.session_id, UUID)

    def test_session_defaults(self):
        session = LearningSession.objects.create()
        assert session.is_active is True
        assert session.current_phoneme is None
        assert session.started_at is not None
        assert session.last_active_at is not None

    def test_assign_phoneme_fk(self):
        phoneme = Phoneme.objects.create(symbol="zz", category="digraph")
        session = LearningSession.objects.create(current_phoneme=phoneme)
        session.refresh_from_db()
        assert session.current_phoneme == phoneme

    def test_phoneme_delete_sets_null(self):
        phoneme = Phoneme.objects.create(symbol="xx", category="digraph")
        session = LearningSession.objects.create(current_phoneme=phoneme)
        phoneme.delete()
        session.refresh_from_db()
        assert session.current_phoneme is None

    def test_last_active_at_updates_on_save(self):
        session = LearningSession.objects.create()
        original = session.last_active_at
        session.is_active = False
        session.save()
        session.refresh_from_db()
        assert session.last_active_at >= original
