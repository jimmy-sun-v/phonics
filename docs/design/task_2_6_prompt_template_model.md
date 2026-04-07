# Design: Task 2.6 – PromptTemplate Model & Migration

## Overview

Define the `PromptTemplate` model in the `ai_tutor` app for storing configurable system prompts and user context templates with placeholder variables.

## Dependencies

- Task 1.5 (ai_tutor app skeleton)

## Detailed Design

### Model Definition

**File: `apps/ai_tutor/models.py`**

```python
from django.db import models


class PromptTemplate(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique identifier for this template, e.g., 'phonics_feedback'",
    )
    system_prompt = models.TextField(
        help_text="System-level prompt defining the AI tutor's behavior and constraints",
    )
    user_template = models.TextField(
        help_text="User message template with placeholders: {phoneme}, {confidence}, {error}, {attempts}",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this template is currently in use",
    )
    version = models.PositiveIntegerField(
        default=1,
        help_text="Version number for tracking template changes",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_active", "-version"]
        verbose_name = "Prompt Template"
        verbose_name_plural = "Prompt Templates"

    def __str__(self):
        return f"{self.name} v{self.version} ({'active' if self.is_active else 'inactive'})"

    def render(self, phoneme: str, confidence: float, error: str | None, attempts: int) -> list[dict]:
        """Render the template into LLM message format.

        Returns:
            List of message dicts: [{"role": "system", ...}, {"role": "user", ...}]

        Raises:
            KeyError: If a required placeholder is missing from the template.
        """
        user_message = self.user_template.format(
            phoneme=phoneme,
            confidence=confidence,
            error=error or "none",
            attempts=attempts,
        )
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message},
        ]
```

### Design Decisions

- **`name` unique**: Each template is identified by a unique name. The service layer retrieves the active template by name.
- **`render()` method**: Convenience method on the model itself for simple placeholder interpolation. Uses Python's `str.format()`.
- **`version` field**: Allows tracking changes. When updating a template, create a new version and deactivate the old one.
- **Active template enforcement**: The service layer (Task 3.7) will ensure only one active template per name is used at query time, using `filter(name=..., is_active=True).order_by('-version').first()`.
- **No complex Jinja2 or template engine**: `str.format()` is sufficient for the simple placeholder pattern.

### Admin Registration

**File: `apps/ai_tutor/admin.py`**

```python
from django.contrib import admin
from .models import PromptTemplate


@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
```

### Database Schema

Table: `ai_tutor_prompttemplate`

| Column | Type | Constraints |
|--------|------|-------------|
| id | bigint | PK, auto-increment |
| name | varchar(100) | UNIQUE, NOT NULL |
| system_prompt | text | NOT NULL |
| user_template | text | NOT NULL |
| is_active | boolean | NOT NULL, default true, indexed |
| version | integer | NOT NULL, default 1, positive |
| created_at | timestamp with tz | NOT NULL, auto |
| updated_at | timestamp with tz | NOT NULL, auto |

## Acceptance Criteria

- [ ] Template created with placeholder syntax
- [ ] `render(phoneme="/sh/", confidence=0.61, error="/s/", attempts=3)` returns correct message list
- [ ] Unique name constraint enforced
- [ ] `is_active` filterable
- [ ] Version is a positive integer

## Test Strategy

**File: `apps/ai_tutor/tests/test_models.py`**

```python
import pytest
from django.db import IntegrityError
from apps.ai_tutor.models import PromptTemplate


@pytest.mark.django_db
class TestPromptTemplateModel:
    def test_create_template(self):
        tpl = PromptTemplate.objects.create(
            name="phonics_feedback",
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
```
