from unittest.mock import patch

import pytest

from apps.ai_tutor.models import PromptTemplate
from apps.games.models import StorySession
from apps.sessions.models import LearningSession


@pytest.mark.django_db
class TestStoryTurnAPI:
    @pytest.fixture
    def session(self):
        return LearningSession.objects.create()

    @pytest.fixture
    def story_template(self):
        tpl, _ = PromptTemplate.objects.get_or_create(
            name="story_builder",
            version=1,
            defaults={
                "system_prompt": "You are a storytelling buddy.",
                "user_template": (
                    "Story so far:\n{story_so_far}\n\n"
                    "The child just said: \"{child_text}\"\n\n"
                    "Round {round_number} of {total_rounds}.\n"
                    "{instruction}"
                ),
                "is_active": True,
            },
        )
        return tpl

    @patch("apps.games.story_views.call_llm")
    def test_first_turn_creates_story_session(self, mock_llm, client, session, story_template):
        mock_llm.return_value = _llm_ok("The bird flew high! What happened next?")

        response = client.post(
            "/api/games/story/turn/",
            {"session_id": str(session.session_id), "text": "Once upon a time there was a bird."},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["story_session_id"] is not None
        assert data["round_number"] == 1
        assert data["is_complete"] is False
        assert data["llm_response"] == "The bird flew high! What happened next?"

    @patch("apps.games.story_views.call_llm")
    def test_subsequent_turn_continues_story(self, mock_llm, client, session, story_template):
        mock_llm.return_value = _llm_ok("The bird flew high! What happened next?")

        # First turn
        r1 = client.post(
            "/api/games/story/turn/",
            {"session_id": str(session.session_id), "text": "Once upon a time there was a bird."},
            content_type="application/json",
        )
        story_id = r1.json()["story_session_id"]

        # Second turn
        mock_llm.return_value = _llm_ok("The bird found a friend! Then what?")
        r2 = client.post(
            "/api/games/story/turn/",
            {
                "session_id": str(session.session_id),
                "story_session_id": story_id,
                "text": "The bird met a cat.",
            },
            content_type="application/json",
        )

        assert r2.status_code == 200
        data = r2.json()
        assert data["round_number"] == 2
        assert data["is_complete"] is False

    @patch("apps.games.story_views.call_llm")
    def test_final_round_completes_story(self, mock_llm, client, session, story_template):
        story = StorySession.objects.create(
            session=session,
            max_rounds=2,
            turns=[
                {"role": "child", "text": "Once upon a time."},
                {"role": "llm", "text": "There was a cat."},
            ],
        )

        # Mock both the continuation and summary calls
        mock_llm.side_effect = [
            _llm_ok("And they lived happily ever after!"),
            _llm_ok("A child and a cat had a wonderful adventure."),
        ]

        response = client.post(
            "/api/games/story/turn/",
            {
                "session_id": str(session.session_id),
                "story_session_id": story.pk,
                "text": "They played together.",
            },
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_complete"] is True
        assert data["round_number"] == 2
        assert len(data["summary"]) > 0

    @patch("apps.games.story_views.call_llm")
    def test_completed_story_rejects_new_turns(self, mock_llm, client, session, story_template):
        story = StorySession.objects.create(
            session=session,
            max_rounds=1,
            is_complete=True,
            turns=[
                {"role": "child", "text": "Once."},
                {"role": "llm", "text": "The end."},
            ],
        )

        response = client.post(
            "/api/games/story/turn/",
            {
                "session_id": str(session.session_id),
                "story_session_id": story.pk,
                "text": "More story!",
            },
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_missing_session_returns_404(self, client, story_template):
        response = client.post(
            "/api/games/story/turn/",
            {"session_id": "00000000-0000-0000-0000-000000000000", "text": "Hello"},
            content_type="application/json",
        )
        assert response.status_code == 404

    def test_missing_text_returns_400(self, client, session, story_template):
        response = client.post(
            "/api/games/story/turn/",
            {"session_id": str(session.session_id)},
            content_type="application/json",
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestStorySessionModel:
    def test_child_turn_count(self):
        session = LearningSession.objects.create()
        story = StorySession.objects.create(
            session=session,
            turns=[
                {"role": "child", "text": "Hello"},
                {"role": "llm", "text": "Hi there!"},
                {"role": "child", "text": "What next?"},
            ],
        )
        assert story.child_turn_count == 2
        assert story.round_number == 2

    def test_empty_turns(self):
        session = LearningSession.objects.create()
        story = StorySession.objects.create(session=session)
        assert story.child_turn_count == 0
        assert story.round_number == 0

    def test_cascade_on_session_delete(self):
        session = LearningSession.objects.create()
        StorySession.objects.create(session=session)
        session.delete()
        assert StorySession.objects.count() == 0


def _llm_ok(text):
    from apps.ai_tutor.llm_client import LLMResponse
    return LLMResponse(text=text, is_successful=True)
