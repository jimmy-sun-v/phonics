import json
from pathlib import Path

from django.db import migrations


def seed_phonemes(apps, schema_editor):
    Phoneme = apps.get_model("phonics", "Phoneme")
    data_file = Path(__file__).resolve().parent.parent / "data" / "phonemes.json"
    with open(data_file) as f:
        phonemes = json.load(f)

    for item in phonemes:
        Phoneme.objects.update_or_create(
            symbol=item["symbol"],
            defaults={
                "category": item["category"],
                "example_words": item["example_words"],
                "display_order": item["display_order"],
            },
        )


def reverse_seed(apps, schema_editor):
    Phoneme = apps.get_model("phonics", "Phoneme")
    Phoneme.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("phonics", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_phonemes, reverse_seed),
    ]
