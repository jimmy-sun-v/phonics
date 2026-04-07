import json
from pathlib import Path

from django.db import migrations


def seed_prompts(apps, schema_editor):
    PromptTemplate = apps.get_model("ai_tutor", "PromptTemplate")
    data_file = Path(__file__).resolve().parent.parent / "data" / "default_prompts.json"
    with open(data_file) as f:
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
