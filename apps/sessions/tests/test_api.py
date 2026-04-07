from uuid import uuid4

import pytest
from rest_framework.test import APIClient

from apps.sessions.models import LearningSession


@pytest.mark.django_db
class TestSessionAPI:
    @pytest.fixture
    def client(self):
        return APIClient()

    def test_create_session(self, client):
        response = client.post("/api/sessions/")
        assert response.status_code == 201
        assert "session_id" in response.data
        assert response.data["is_active"] is True

    def test_get_session(self, client):
        session = LearningSession.objects.create()
        response = client.get(f"/api/sessions/{session.session_id}/")
        assert response.status_code == 200
        assert response.data["session_id"] == str(session.session_id)

    def test_get_session_not_found(self, client):
        response = client.get(f"/api/sessions/{uuid4()}/")
        assert response.status_code == 404

    def test_update_phoneme(self, client):
        session = LearningSession.objects.create()
        response = client.patch(
            f"/api/sessions/{session.session_id}/",
            {"phoneme": "sh"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["current_phoneme_symbol"] == "sh"

    def test_update_inactive_session(self, client):
        session = LearningSession.objects.create(is_active=False)
        response = client.patch(
            f"/api/sessions/{session.session_id}/",
            {"phoneme": "sh"},
            format="json",
        )
        assert response.status_code == 409
