# Design: Task 2.7 – Seed Default AI Prompt Templates

## Overview

Create a data migration to seed the default prompt template from the App_Overview §8, including the system prompt with child-safety rules and the user context template with placeholders.

## Dependencies

- Task 2.6 (PromptTemplate model)

## Detailed Design

### Default Prompt Data

**File: `apps/ai_tutor/data/default_prompts.json`**

```json
[
  {
    "name": "phonics_feedback",
    "version": 1,
    "is_active": true,
    "system_prompt": "You are a friendly phonics tutor for children aged 5-7.\n\nYou MUST follow these rules:\n- Use simple words that a 5-year-old can understand\n- Be encouraging and positive at all times\n- NEVER use the word \"wrong\" or any negative language\n- NEVER ask personal questions (name, age, location, family)\n- NEVER ask open-ended questions\n- Respond in 1-2 short sentences ONLY\n- Focus only on the phoneme being practiced\n- If the child is struggling, offer gentle guidance\n- Always acknowledge effort before giving guidance\n- Use phrases like \"Great try!\", \"Almost there!\", \"Let's try again!\"",
    "user_template": "The child is practicing the phoneme {phoneme}.\n\nSpeech recognition results:\n- Confidence score: {confidence}\n- Detected error: {error}\n- Attempt number: {attempts}\n\nProvide brief, encouraging feedback appropriate for a 5-7 year old."
  }
]
```

### Data Migration

**File: `apps/ai_tutor/migrations/0002_seed_default_prompts.py`**

```python
import json
from pathlib import Path
from django.db import migrations


def seed_prompts(apps, schema_editor):
    PromptTemplate = apps.get_model("ai_tutor", "PromptTemplate")
    data_file = Path(__file__).resolve().parent.parent / "data" / "default_prompts.json"
    with open(data_file, "r") as f:
        prompts = json.load(f)

    for item in prompts:
        PromptTemplate.objects.update_or_create(
            name=item["name"],
            defaults={
                "system_prompt": item["system_prompt"],
                "user_template": item["user_template"],
                "is_active": item["is_active"],
                "version": item["version"],
            },
        )


def reverse_seed(apps, schema_editor):
    PromptTemplate = apps.get_model("ai_tutor", "PromptTemplate")
    PromptTemplate.objects.filter(name="phonics_feedback").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("ai_tutor", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_prompts, reverse_seed),
    ]
```

### System Prompt Safety Rules Mapping

The system prompt enforces the following rules from App_Overview §4.1 and §8:

| Rule | System Prompt Line |
|------|-------------------|
| Simple words | "Use simple words that a 5-year-old can understand" |
| Encouraging | "Be encouraging and positive at all times" |
| No "wrong" | "NEVER use the word 'wrong' or any negative language" |
| No personal questions | "NEVER ask personal questions (name, age, location, family)" |
| Short responses | "Respond in 1-2 short sentences ONLY" |
| No open-ended questions | "NEVER ask open-ended questions" |
| Acknowledge effort | "Always acknowledge effort before giving guidance" |

### User Template Placeholders

| Placeholder | Source | Example |
|-------------|--------|---------|
| `{phoneme}` | Current phoneme symbol | `/sh/` |
| `{confidence}` | Azure STT confidence score | `0.61` |
| `{error}` | Detected substitution error or "none" | `/s/` |
| `{attempts}` | Number of attempts for this phoneme | `3` |

## Acceptance Criteria

- [ ] `phonics_feedback` template exists in DB after migration
- [ ] System prompt contains all safety rules
- [ ] User template has all 4 placeholders: `{phoneme}`, `{confidence}`, `{error}`, `{attempts}`
- [ ] `template.render(...)` produces valid messages
- [ ] Seed is idempotent (re-runnable via `update_or_create`)

## Test Strategy

**File: `apps/ai_tutor/tests/test_seed_prompts.py`**

```python
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
        assert "wrong" in tpl.system_prompt.lower()  # rule about "wrong"
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
```
