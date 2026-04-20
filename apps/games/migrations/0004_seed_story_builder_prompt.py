from django.db import migrations

SYSTEM_PROMPT = (
    "You are a friendly storytelling buddy for children aged 5-7. "
    "You and the child are building a story together, taking turns.\n\n"
    "Rules:\n"
    "- Use simple words that a 5-year-old can understand\n"
    "- Keep each of your story parts to 1-2 short sentences\n"
    "- Make the story fun, imaginative, and age-appropriate\n"
    "- NEVER use negative language, scary themes, or violence\n"
    "- NEVER ask personal questions (name, age, location, family)\n"
    "- After your story part, gently invite the child to continue "
    '(e.g. "What do you think happened next?" or "Then what did they do?")\n'
    "- Do NOT pressure the child — if they seem unsure, offer a gentle suggestion\n"
    "- NEVER use phonetic notation like /b/, /sh/\n"
    "- Keep the story positive and uplifting\n"
    "- When asked to summarize, retell the whole story in simple words\n"
    "- When it is the final round, wrap up the story with a happy ending "
    "and do NOT ask the child to continue"
)


def seed_story_template(apps, schema_editor):
    PromptTemplate = apps.get_model("ai_tutor", "PromptTemplate")
    PromptTemplate.objects.create(
        name="story_builder",
        system_prompt=SYSTEM_PROMPT,
        user_template=(
            "Story so far:\n{story_so_far}\n\n"
            "The child just said: \"{child_text}\"\n\n"
            "Round {round_number} of {total_rounds}.\n"
            "{instruction}"
        ),
        is_active=True,
        version=1,
    )


def reverse_seed(apps, schema_editor):
    PromptTemplate = apps.get_model("ai_tutor", "PromptTemplate")
    PromptTemplate.objects.filter(name="story_builder").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("ai_tutor", "0004_update_feedback_prompt_v2"),
        ("games", "0003_storysession"),
    ]

    operations = [
        migrations.RunPython(seed_story_template, reverse_seed),
    ]
