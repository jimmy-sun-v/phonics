import pytest

from apps.ai_tutor.models import PromptTemplate
from apps.ai_tutor.services import TemplateNotFoundError, get_active_template, render_prompt


@pytest.mark.django_db
class TestPromptRendering:
    @pytest.fixture(autouse=True)
    def create_template(self):
        # Deactivate seeded template to avoid conflicts
        PromptTemplate.objects.filter(name="phonics_feedback").update(is_active=False)
        PromptTemplate.objects.create(
            name="phonics_feedback",
            system_prompt="You are a tutor.",
            user_template="Phoneme: {phoneme}, Conf: {confidence}, Error: {error}, Attempts: {attempts}",
            is_active=True,
            version=10,
        )

    def test_render_with_all_variables(self):
        messages = render_prompt(phoneme="/sh/", confidence=0.61, error="/s/", attempts=3)
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert "/sh/" in messages[1]["content"]
        assert "0.61" in messages[1]["content"]
        assert "/s/" in messages[1]["content"]
        assert "3" in messages[1]["content"]

    def test_render_with_no_error(self):
        messages = render_prompt(phoneme="/th/", confidence=0.9, error=None, attempts=1)
        assert "none" in messages[1]["content"]

    def test_inactive_template_not_returned(self):
        PromptTemplate.objects.filter(name="phonics_feedback").update(is_active=False)
        with pytest.raises(TemplateNotFoundError):
            render_prompt(phoneme="/sh/", confidence=0.5, error=None, attempts=1)

    def test_latest_version_used(self):
        PromptTemplate.objects.create(
            name="phonics_feedback",
            system_prompt="Updated tutor.",
            user_template="{phoneme} {confidence} {error} {attempts}",
            is_active=True,
            version=20,
        )
        template = get_active_template("phonics_feedback")
        assert template.version == 20
        assert template.system_prompt == "Updated tutor."

    def test_missing_template_raises(self):
        with pytest.raises(TemplateNotFoundError):
            get_active_template("nonexistent")
