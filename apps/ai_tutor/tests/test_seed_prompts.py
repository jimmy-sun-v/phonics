import pytest

from apps.ai_tutor.models import PromptTemplate


@pytest.mark.django_db
class TestDefaultPromptSeed:
    def test_template_exists(self):
        tpl = PromptTemplate.objects.filter(name="phonics_feedback", is_active=True).order_by("-version").first()
        assert tpl is not None
        assert tpl.is_active is True
        assert tpl.version == 2

    def test_system_prompt_safety_rules(self):
        tpl = PromptTemplate.objects.filter(name="phonics_feedback", is_active=True).order_by("-version").first()
        assert "wrong" in tpl.system_prompt.lower()
        assert "personal questions" in tpl.system_prompt.lower()
        assert "no more than 10 words" in tpl.system_prompt.lower()

    def test_system_prompt_score_guidance(self):
        tpl = PromptTemplate.objects.filter(name="phonics_feedback", is_active=True).order_by("-version").first()
        assert "80-100" in tpl.system_prompt
        assert "50-79" in tpl.system_prompt
        assert "below 50" in tpl.system_prompt.lower()

    def test_user_template_has_placeholders(self):
        tpl = PromptTemplate.objects.filter(name="phonics_feedback", is_active=True).order_by("-version").first()
        assert "{phoneme}" in tpl.user_template
        assert "{confidence}" in tpl.user_template
        assert "{error}" in tpl.user_template
        assert "{attempts}" in tpl.user_template

    def test_render_works(self):
        tpl = PromptTemplate.objects.filter(name="phonics_feedback", is_active=True).order_by("-version").first()
        messages = tpl.render(phoneme="/sh/", confidence=61, error="/s/", attempts=3)
        assert len(messages) == 2
        assert "/sh/" in messages[1]["content"]
