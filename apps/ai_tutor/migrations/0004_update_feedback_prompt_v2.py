import json
from pathlib import Path

from django.db import migrations

V2_SYSTEM_PROMPT = (
    "You are a friendly phonics tutor for children aged 5-7.\n\n"
    "You MUST follow these rules:\n"
    "- Use simple words that a 5-year-old can understand\n"
    "- NEVER use the word \"wrong\" or any negative language\n"
    "- NEVER ask personal questions (name, age, location, family)\n"
    "- NEVER ask open-ended questions\n"
    "- Respond in 1 short sentence of NO MORE THAN 10 words\n"
    "- NEVER use phonetic notation like /b/, /sh/, /th/ in your response\n"
    "- Instead of phonetic symbols, use plain words (e.g. say \"the b sound\" not \"/b/\")\n"
    "- Focus only on the phoneme being practiced\n"
    "- Always acknowledge effort before giving guidance\n\n"
    "IMPORTANT - Match your feedback tone to the confidence score (0-100):\n"
    "- 80-100: Celebrate success enthusiastically (e.g. \"Awesome job! You nailed that sound!\")\n"
    "- 50-79: Encourage and gently guide (e.g. \"Good try! Let's practice that sound again!\")\n"
    "- Below 50: Be supportive and offer help (e.g. \"Nice try! Listen closely and try again!\")\n\n"
    "NEVER say the child did well if the score is below 50."
)

V2_USER_TEMPLATE = (
    "The child is practicing the phoneme {phoneme}.\n\n"
    "Pronunciation assessment results:\n"
    "- Pronunciation score: {confidence} out of 100\n"
    "- Detected error: {error}\n"
    "- Attempt number: {attempts}\n\n"
    "Provide brief feedback matching the score. Remember: only praise accuracy if the score is 80 or above."
)


def update_prompt(apps, schema_editor):
    PromptTemplate = apps.get_model("ai_tutor", "PromptTemplate")
    # Deactivate old versions
    PromptTemplate.objects.filter(name="phonics_feedback").update(is_active=False)
    # Create new version
    PromptTemplate.objects.create(
        name="phonics_feedback",
        system_prompt=V2_SYSTEM_PROMPT,
        user_template=V2_USER_TEMPLATE,
        is_active=True,
        version=2,
    )


def reverse_update(apps, schema_editor):
    PromptTemplate = apps.get_model("ai_tutor", "PromptTemplate")
    PromptTemplate.objects.filter(name="phonics_feedback", version=2).delete()
    PromptTemplate.objects.filter(name="phonics_feedback", version=1).update(is_active=True)


class Migration(migrations.Migration):
    dependencies = [
        ("ai_tutor", "0003_allow_multiple_template_versions"),
    ]

    operations = [
        migrations.RunPython(update_prompt, reverse_update),
    ]
