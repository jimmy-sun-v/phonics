# Design: Task 3.2 – Session Management Service

## Overview

Create a service layer for managing anonymous learning sessions: creation, retrieval, phoneme updates, and deactivation.

## Dependencies

- Task 2.3 (LearningSession model)

## Detailed Design

### Service Module

**File: `apps/sessions/services.py`**

```python
import logging
from uuid import UUID
from apps.sessions.models import LearningSession
from apps.phonics.models import Phoneme

logger = logging.getLogger(__name__)


class SessionNotFoundError(Exception):
    """Raised when a session ID does not correspond to any session."""
    pass


class SessionInactiveError(Exception):
    """Raised when an operation is attempted on an inactive session."""
    pass


def create_session() -> LearningSession:
    """Create a new anonymous learning session.

    Returns:
        New LearningSession with auto-generated UUID.
    """
    session = LearningSession.objects.create()
    logger.info("Created new session: %s", session.session_id)
    return session


def get_session(session_id: UUID | str) -> LearningSession:
    """Retrieve a session by its UUID.

    Args:
        session_id: UUID string or UUID object.

    Returns:
        LearningSession instance.

    Raises:
        SessionNotFoundError: If session does not exist.
    """
    try:
        return LearningSession.objects.get(session_id=session_id)
    except LearningSession.DoesNotExist:
        raise SessionNotFoundError(f"Session {session_id} not found")


def update_current_phoneme(session_id: UUID | str, phoneme_symbol: str) -> LearningSession:
    """Update the current phoneme for an active session.

    Args:
        session_id: Session UUID.
        phoneme_symbol: Symbol of the phoneme to set as current.

    Returns:
        Updated LearningSession.

    Raises:
        SessionNotFoundError: If session does not exist.
        SessionInactiveError: If session is not active.
        Phoneme.DoesNotExist: If phoneme symbol is invalid.
    """
    session = get_session(session_id)
    if not session.is_active:
        raise SessionInactiveError(f"Session {session_id} is inactive")

    phoneme = Phoneme.objects.get(symbol=phoneme_symbol)
    session.current_phoneme = phoneme
    session.save()  # Triggers last_active_at update
    return session


def deactivate_session(session_id: UUID | str) -> LearningSession:
    """Mark a session as inactive. Inactive sessions cannot be updated.

    Args:
        session_id: Session UUID.

    Returns:
        Deactivated LearningSession.

    Raises:
        SessionNotFoundError: If session does not exist.
    """
    session = get_session(session_id)
    session.is_active = False
    session.save()
    logger.info("Deactivated session: %s", session.session_id)
    return session
```

### Custom Exceptions

- `SessionNotFoundError`: Used instead of Django's `DoesNotExist` to decouple service layer from ORM specifics.
- `SessionInactiveError`: Prevents state changes on closed sessions.

These exceptions are caught in the API view layer (Task 3.12) and translated to appropriate HTTP responses.

## Acceptance Criteria

- [ ] `create_session()` returns session with auto-generated UUID (no PII)
- [ ] `get_session(uuid)` retrieves existing session
- [ ] `get_session(invalid_uuid)` raises `SessionNotFoundError`
- [ ] `update_current_phoneme(id, "sh")` updates the session's phoneme
- [ ] Updating an inactive session raises `SessionInactiveError`
- [ ] `deactivate_session(id)` sets `is_active = False`

## Test Strategy

**File: `apps/sessions/tests/test_services.py`**

```python
import pytest
from uuid import uuid4
from apps.sessions.services import (
    create_session,
    get_session,
    update_current_phoneme,
    deactivate_session,
    SessionNotFoundError,
    SessionInactiveError,
)
from apps.phonics.models import Phoneme


@pytest.mark.django_db
class TestSessionService:
    @pytest.fixture(autouse=True)
    def setup_phoneme(self):
        Phoneme.objects.create(symbol="sh", category="digraph", example_words=["ship"])

    def test_create_session(self):
        session = create_session()
        assert session.session_id is not None
        assert session.is_active is True
        assert session.current_phoneme is None

    def test_get_session(self):
        created = create_session()
        retrieved = get_session(created.session_id)
        assert retrieved.session_id == created.session_id

    def test_get_session_not_found(self):
        with pytest.raises(SessionNotFoundError):
            get_session(uuid4())

    def test_update_current_phoneme(self):
        session = create_session()
        updated = update_current_phoneme(session.session_id, "sh")
        assert updated.current_phoneme.symbol == "sh"

    def test_update_inactive_session_fails(self):
        session = create_session()
        deactivate_session(session.session_id)
        with pytest.raises(SessionInactiveError):
            update_current_phoneme(session.session_id, "sh")

    def test_deactivate_session(self):
        session = create_session()
        deactivated = deactivate_session(session.session_id)
        assert deactivated.is_active is False
```
