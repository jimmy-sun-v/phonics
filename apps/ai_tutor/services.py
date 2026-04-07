import logging

from apps.ai_tutor.models import PromptTemplate

logger = logging.getLogger(__name__)


class TemplateNotFoundError(Exception):
    pass


def get_active_template(name: str = "phonics_feedback") -> PromptTemplate:
    template = PromptTemplate.objects.filter(name=name, is_active=True).order_by("-version").first()
    if template is None:
        raise TemplateNotFoundError(f"No active template found with name '{name}'")
    return template


def render_prompt(
    phoneme: str,
    confidence: float,
    error: str | None,
    attempts: int,
    template_name: str = "phonics_feedback",
) -> list[dict[str, str]]:
    template = get_active_template(template_name)
    try:
        messages = template.render(phoneme=phoneme, confidence=confidence, error=error, attempts=attempts)
        logger.debug("Rendered prompt template '%s' v%d for phoneme %s", template.name, template.version, phoneme)
        return messages
    except KeyError as e:
        logger.error("Template '%s' has unrecognized placeholder: %s", template.name, e)
        raise
