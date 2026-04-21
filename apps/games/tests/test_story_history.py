import pytest

from apps.games.models import StorySession
from apps.sessions.models import LearningSession


def _get_browser_key(client):
    """Ensure the test client has a Django session and return its key."""
    # Make a request to create the session
    if not client.session.session_key:
        client.get("/games/story_builder/history/")
    return client.session.session_key


@pytest.mark.django_db
class TestStoryHistoryListAPI:
    @pytest.fixture
    def session_with_stories(self, client):
        browser_key = _get_browser_key(client)
        ls = LearningSession.objects.create()

        complete = StorySession.objects.create(
            session=ls,
            max_rounds=2,
            is_complete=True,
            summary="A bird and a cat became friends.",
            browser_session_key=browser_key,
            turns=[
                {"role": "child", "text": "Once upon a time."},
                {"role": "llm", "text": "There was a cat."},
                {"role": "child", "text": "The cat met a bird."},
                {"role": "llm", "text": "They became friends!"},
            ],
        )
        incomplete = StorySession.objects.create(
            session=ls,
            max_rounds=4,
            is_complete=False,
            browser_session_key=browser_key,
            turns=[
                {"role": "child", "text": "Hello."},
                {"role": "llm", "text": "Hi there!"},
            ],
        )
        return ls, complete, incomplete

    def test_returns_only_complete_stories(self, client, session_with_stories):
        ls, complete, incomplete = session_with_stories

        response = client.get("/api/games/story/history/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == complete.pk
        assert data[0]["summary"] == "A bird and a cat became friends."
        assert data[0]["round_count"] == 2

    def test_empty_when_no_stories(self, client):
        response = client.get("/api/games/story/history/")
        assert response.status_code == 200
        assert response.json() == []

    def test_does_not_return_other_users_stories(self, client):
        other_ls = LearningSession.objects.create()
        StorySession.objects.create(
            session=other_ls,
            is_complete=True,
            summary="Someone else's story.",
            browser_session_key="other-session-key",
            turns=[{"role": "child", "text": "test"}],
        )

        response = client.get("/api/games/story/history/")
        assert response.status_code == 200
        assert response.json() == []

    def test_auto_claims_unclaimed_stories(self, client):
        """Stories created before session tracking should be auto-claimed."""
        ls = LearningSession.objects.create()
        story = StorySession.objects.create(
            session=ls,
            is_complete=True,
            summary="An old story.",
            browser_session_key="",  # unclaimed
            turns=[{"role": "child", "text": "old"}],
        )

        response = client.get("/api/games/story/history/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == story.pk

        # Verify the story is now claimed
        story.refresh_from_db()
        assert story.browser_session_key != ""


@pytest.mark.django_db
class TestStoryHistoryDetailAPI:
    @pytest.fixture
    def complete_story(self, client):
        browser_key = _get_browser_key(client)
        ls = LearningSession.objects.create()

        story = StorySession.objects.create(
            session=ls,
            max_rounds=2,
            is_complete=True,
            summary="A wonderful adventure!",
            browser_session_key=browser_key,
            turns=[
                {"role": "child", "text": "Once upon a time."},
                {"role": "llm", "text": "There was a dragon."},
                {"role": "child", "text": "The dragon was friendly."},
                {"role": "llm", "text": "They had tea together!"},
            ],
        )
        return story

    def test_returns_full_story_detail(self, client, complete_story):
        response = client.get(f"/api/games/story/history/{complete_story.pk}/")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == complete_story.pk
        assert len(data["turns"]) == 4
        assert data["summary"] == "A wonderful adventure!"
        assert data["round_count"] == 2

    def test_returns_404_for_unknown_story(self, client, complete_story):
        response = client.get("/api/games/story/history/99999/")
        assert response.status_code == 404

    def test_returns_404_for_other_users_story(self, client):
        other_ls = LearningSession.objects.create()
        story = StorySession.objects.create(
            session=other_ls,
            is_complete=True,
            browser_session_key="other-session-key",
            turns=[{"role": "child", "text": "test"}],
        )

        response = client.get(f"/api/games/story/history/{story.pk}/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestStoryHistoryPageViews:
    def test_history_page_loads(self, client):
        response = client.get("/games/story_builder/history/")
        assert response.status_code == 200
        assert b"My Stories" in response.content

    def test_detail_page_loads(self, client):
        ls = LearningSession.objects.create()
        story = StorySession.objects.create(
            session=ls,
            is_complete=True,
            turns=[{"role": "child", "text": "test"}],
        )
        response = client.get(f"/games/story_builder/history/{story.pk}/")
        assert response.status_code == 200

    def test_story_builder_tracks_session_id(self, client):
        response = client.get("/games/story_builder/")
        assert response.status_code == 200
        session_ids = client.session.get("story_learning_session_ids", [])
        assert len(session_ids) == 1
