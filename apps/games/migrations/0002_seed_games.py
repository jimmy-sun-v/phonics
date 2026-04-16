import json
from pathlib import Path

from django.db import migrations


def seed_games(apps, schema_editor):
    Game = apps.get_model("games", "Game")
    GamePhonemeMapping = apps.get_model("games", "GamePhonemeMapping")
    Phoneme = apps.get_model("phonics", "Phoneme")

    data_file = Path(__file__).resolve().parent.parent / "data" / "games_seed.json"
    with open(data_file) as f:
        games_data = json.load(f)

    for item in games_data:
        game, _created = Game.objects.update_or_create(
            game_type=item["game_type"],
            defaults={
                "name": item["name"],
                "description": item["description"],
                "is_active": True,
            },
        )

        phonemes = Phoneme.objects.filter(category__in=item["categories"])
        for phoneme in phonemes:
            GamePhonemeMapping.objects.get_or_create(
                game=game,
                phoneme=phoneme,
            )


def reverse_seed(apps, schema_editor):
    Game = apps.get_model("games", "Game")
    Game.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("games", "0001_initial"),
        ("phonics", "0002_seed_phonemes"),
    ]

    operations = [
        migrations.RunPython(seed_games, reverse_seed),
    ]
