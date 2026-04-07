# Design: Task 3.7 – AI Tutor – Prompt Rendering Service

## Overview

Create a service that loads the active PromptTemplate from the database, renders it with provided context variables, and returns formatted messages ready for LLM submission.

## Dependencies

- Task 2.6 (PromptTemplate model)
- Task 2.7 (Seed prompt data)

## Detailed Design

### Service Module

**File: `apps/ai_tutor/services.py`**

```python
import logging
from apps.ai_tutor.models import PromptTemplate

logger = logging.getLogger(__name__)


class TemplateNotFoundError(Exception):
    """Raised when no active prompt template is found."""
    pass


def get_active_template(name: str = "phonics_feedback") -> PromptTemplate:
    """Retrieve the active prompt template by name.

    If multiple active templates exist with the same name,
    returns the one with the highest version.

    Args:
        name: Template name to look up.

    Returns:
        Active PromptTemplate instance.

    Raises:
        TemplateNotFoundError: If no active template with the given name exists.
    """
    template = (
        PromptTemplate.objects
        .filter(name=name, is_active=True)
        .order_by("-version")
        .first()
    )
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
    """Render a prompt template with the given context variables.

    Args:
        phoneme: The phoneme being practiced (e.g., "/sh/").
        confidence: STT confidence score (0.0–1.0).
        error: Detected substitution error or None.
        attempts: Number of attempts for this phoneme.
        template_name: Name of the template to use.

    Returns:
        List of message dicts: [{"role": "system", ...}, {"role": "user", ...}]

    Raises:
        TemplateNotFoundError: If no active template found.
        KeyError: If template contains unrecognized placeholders.
    """
    template = get_active_template(template_name)
    try:
        messages = template.render(
            phoneme=phoneme,
            confidence=confidence,
            error=error,
            attempts=attempts,
        )
        logger.debug(
            "Rendered prompt template '%s' v%d for phoneme %s",
            template.name, template.version, phoneme,
        )
        return messages
    except KeyError as e:
        logger.error("Template '%s' has unrecognized placeholder: %s", template.name, e)
        raise
```

### Integration Flow

```
Feedback Strategy (Task 3.10)
    ↓ provides: phoneme, confidence, error, attempts
Prompt Rendering Service (this task)
    ↓ provides: formatted messages
Azure OpenAI Client (Task 3.8)
    ↓ sends to LLM
Response Validator (Task 3.9)
    ↓ returns: safe feedback text
```

## Acceptance Criteria

- [ ] Active template loaded from database by name
- [ ] Variables correctly interpolated into template
- [ ] Output is `[{"role": "system", ...}, {"role": "user", ...}]`
- [ ] Missing template raises `TemplateNotFoundError`
- [ ] Unrecognized placeholder raises `KeyError`
- [ ] Inactive templates are not returned

## Test Strategy

**File: `apps/ai_tutor/tests/test_prompt_rendering.py`**

```python
import pytest
from apps.ai_tutor.models import PromptTemplate
from apps.ai_tutor.services import render_prompt, get_active_template, TemplateNotFoundError


@pytest.mark.django_db
class TestPromptRendering:
    @pytest.fixture(autouse=True)
    def create_template(self):
        PromptTemplate.objects.create(
            name="phonics_feedback",
            system_prompt="You are a tutor.",
            user_template="Phoneme: {phoneme}, Conf: {confidence}, Error: {error}, Attempts: {attempts}",
            is_active=True,
            version=1,
        )

    def test_render_with_all_variables(self):
        messages = render_prompt(
            phoneme="/sh/", confidence=0.61, error="/s/", attempts=3
        )
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
            version=2,
        )
        template = get_active_template("phonics_feedback")
        assert template.version == 2
        assert template.system_prompt == "Updated tutor."

    def test_missing_template_raises(self):
        with pytest.raises(TemplateNotFoundError):
            get_active_template("nonexistent")
```
