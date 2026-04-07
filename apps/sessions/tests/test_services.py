from uuid import uuid4

import pytest

from apps.phonics.models import Phoneme
from apps.sessions.services import (
    SessionInactiveError,
    SessionNotFoundError,
    create_session,
    deactivate_session,
    get_session,
    update_current_phoneme,
)


@pytest.mark.django_db
class TestSessionService:
    @pytest.fixture(autouse=True)
    def setup_phoneme(self):
        Phoneme.objects.get_or_create(symbol="sh", defaults={"category": "digraph", "example_words": ["ship"]})

    def test_create_session(self):
        session = create_session()
        assert session.session_id is not None
        assert session.is_active is True

    def test_get_session(self):
        session = create_session()
        found = get_session(session.session_id)
        assert found.session_id == session.session_id

    def test_get_session_not_found(self):
        with pytest.raises(SessionNotFoundError):
            get_session(uuid4())

    def test_update_current_phoneme(self):
        session = create_session()
        updated = update_current_phoneme(session.session_id, "sh")
        assert updated.current_phoneme.symbol == "sh"

    def test_update_inactive_session_raises(self):
        session = create_session()
        deactivate_session(session.session_id)
        with pytest.raises(SessionInactiveError):
            update_current_phoneme(session.session_id, "sh")

    def test_deactivate_session(self):
        session = create_session()
        deactivated = deactivate_session(session.session_id)
        assert deactivated.is_active is False
