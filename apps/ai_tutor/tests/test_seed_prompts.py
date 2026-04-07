import pytest

from apps.ai_tutor.models import PromptTemplate


@pytest.mark.django_db
class TestDefaultPromptSeed:
    def test_template_exists(self):
        tpl = PromptTemplate.objects.get(name="phonics_feedback")
        assert tpl.is_active is True
        assert tpl.version == 1

    def test_system_prompt_safety_rules(self):
        tpl = PromptTemplate.objects.get(name="phonics_feedback")
        assert "wrong" in tpl.system_prompt.lower()
        assert "personal questions" in tpl.system_prompt.lower()
        assert "1-2 short sentences" in tpl.system_prompt.lower()
        assert "encouraging" in tpl.system_prompt.lower()

    def test_user_template_has_placeholders(self):
        tpl = PromptTemplate.objects.get(name="phonics_feedback")
        assert "{phoneme}" in tpl.user_template
        assert "{confidence}" in tpl.user_template
        assert "{error}" in tpl.user_template
        assert "{attempts}" in tpl.user_template

    def test_render_works(self):
        tpl = PromptTemplate.objects.get(name="phonics_feedback")
        messages = tpl.render(phoneme="/sh/", confidence=0.61, error="/s/", attempts=3)
        assert len(messages) == 2
        assert "/sh/" in messages[1]["content"]
