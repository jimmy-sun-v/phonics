import pytest
from django.db import IntegrityError

from apps.ai_tutor.models import PromptTemplate


@pytest.mark.django_db
class TestPromptTemplateModel:
    def test_create_template(self):
        tpl = PromptTemplate.objects.create(
            name="test_feedback",
            system_prompt="You are a friendly phonics tutor.",
            user_template="The child is practicing {phoneme}. Confidence: {confidence}. Error: {error}. Attempts: {attempts}.",
        )
        assert tpl.pk is not None
        assert tpl.version == 1
        assert tpl.is_active is True

    def test_render_template(self):
        tpl = PromptTemplate(
            name="test",
            system_prompt="You are a tutor.",
            user_template="Phoneme: {phoneme}, Conf: {confidence}, Err: {error}, Att: {attempts}",
        )
        messages = tpl.render(phoneme="/sh/", confidence=0.61, error="/s/", attempts=3)
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "You are a tutor."
        assert messages[1]["role"] == "user"
        assert "/sh/" in messages[1]["content"]
        assert "0.61" in messages[1]["content"]

    def test_render_with_no_error(self):
        tpl = PromptTemplate(
            name="test",
            system_prompt="Tutor",
            user_template="Error: {error}",
        )
        messages = tpl.render(phoneme="sh", confidence=0.9, error=None, attempts=1)
        assert "none" in messages[1]["content"]

    def test_unique_name(self):
        PromptTemplate.objects.create(name="feedback", system_prompt="a", user_template="b")
        with pytest.raises(IntegrityError):
            PromptTemplate.objects.create(name="feedback", system_prompt="c", user_template="d")
