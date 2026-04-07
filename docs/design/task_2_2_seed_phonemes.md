# Design: Task 2.2 – Phonics Seed Data – All Categories

## Overview

Create a data migration that seeds all phoneme categories from the App_Overview specification. The seed data is stored in a JSON file and loaded via a Django data migration for idempotent execution.

## Dependencies

- Task 2.1 (Phoneme model)

## Detailed Design

### Data Source File

**File: `apps/phonics/data/phonemes.json`**

```json
[
  {"symbol": "b", "category": "single_letter", "example_words": ["bat", "big", "bus"], "display_order": 1},
  {"symbol": "c", "category": "single_letter", "example_words": ["cat", "cup", "car"], "display_order": 2},
  {"symbol": "d", "category": "single_letter", "example_words": ["dog", "dig", "day"], "display_order": 3},
  {"symbol": "f", "category": "single_letter", "example_words": ["fan", "fun", "fox"], "display_order": 4},
  {"symbol": "g", "category": "single_letter", "example_words": ["go", "got", "gap"], "display_order": 5},
  {"symbol": "h", "category": "single_letter", "example_words": ["hat", "hen", "hug"], "display_order": 6},
  {"symbol": "j", "category": "single_letter", "example_words": ["jam", "jet", "jog"], "display_order": 7},
  {"symbol": "k", "category": "single_letter", "example_words": ["kite", "kid", "key"], "display_order": 8},
  {"symbol": "l", "category": "single_letter", "example_words": ["lip", "log", "let"], "display_order": 9},
  {"symbol": "m", "category": "single_letter", "example_words": ["map", "mom", "mix"], "display_order": 10},
  {"symbol": "n", "category": "single_letter", "example_words": ["nap", "net", "nut"], "display_order": 11},
  {"symbol": "p", "category": "single_letter", "example_words": ["pan", "pet", "pig"], "display_order": 12},
  {"symbol": "r", "category": "single_letter", "example_words": ["run", "red", "rat"], "display_order": 13},
  {"symbol": "s", "category": "single_letter", "example_words": ["sun", "sit", "sad"], "display_order": 14},
  {"symbol": "t", "category": "single_letter", "example_words": ["top", "ten", "tap"], "display_order": 15},
  {"symbol": "v", "category": "single_letter", "example_words": ["van", "vet", "vine"], "display_order": 16},
  {"symbol": "w", "category": "single_letter", "example_words": ["win", "wet", "wag"], "display_order": 17},
  {"symbol": "y", "category": "single_letter", "example_words": ["yes", "yam", "yell"], "display_order": 18},
  {"symbol": "z", "category": "single_letter", "example_words": ["zip", "zoo", "zig"], "display_order": 19},
  {"symbol": "a", "category": "single_letter", "example_words": ["ant", "apple", "at"], "display_order": 20},
  {"symbol": "e", "category": "single_letter", "example_words": ["egg", "elf", "end"], "display_order": 21},
  {"symbol": "i", "category": "single_letter", "example_words": ["it", "in", "igloo"], "display_order": 22},
  {"symbol": "o", "category": "single_letter", "example_words": ["on", "ox", "otter"], "display_order": 23},
  {"symbol": "u", "category": "single_letter", "example_words": ["up", "us", "umbrella"], "display_order": 24},

  {"symbol": "ch", "category": "digraph", "example_words": ["chip", "chat", "chin"], "display_order": 1},
  {"symbol": "sh", "category": "digraph", "example_words": ["ship", "shop", "shell"], "display_order": 2},
  {"symbol": "th", "category": "digraph", "example_words": ["this", "that", "thin"], "display_order": 3},
  {"symbol": "wh", "category": "digraph", "example_words": ["when", "what", "whale"], "display_order": 4},
  {"symbol": "ph", "category": "digraph", "example_words": ["phone", "photo"], "display_order": 5},
  {"symbol": "ng", "category": "digraph", "example_words": ["ring", "sing", "king"], "display_order": 6},
  {"symbol": "kn", "category": "digraph", "example_words": ["knee", "knot", "know"], "display_order": 7},
  {"symbol": "wr", "category": "digraph", "example_words": ["write", "wrap", "wren"], "display_order": 8},

  {"symbol": "bl", "category": "blend", "example_words": ["blue", "black", "blend"], "display_order": 1},
  {"symbol": "cl", "category": "blend", "example_words": ["clap", "clip", "clay"], "display_order": 2},
  {"symbol": "fl", "category": "blend", "example_words": ["flag", "fly", "flip"], "display_order": 3},
  {"symbol": "gr", "category": "blend", "example_words": ["green", "grab", "grin"], "display_order": 4},
  {"symbol": "st", "category": "blend", "example_words": ["stop", "star", "step"], "display_order": 5},
  {"symbol": "tr", "category": "blend", "example_words": ["tree", "trip", "trap"], "display_order": 6},
  {"symbol": "mp", "category": "blend", "example_words": ["jump", "lamp", "camp"], "display_order": 7},
  {"symbol": "nd", "category": "blend", "example_words": ["hand", "sand", "bend"], "display_order": 8},
  {"symbol": "nk", "category": "blend", "example_words": ["pink", "tank", "sink"], "display_order": 9},

  {"symbol": "a_e", "category": "long_vowel", "example_words": ["cake", "make", "lake"], "display_order": 1},
  {"symbol": "i_e", "category": "long_vowel", "example_words": ["bike", "kite", "like"], "display_order": 2},
  {"symbol": "o_e", "category": "long_vowel", "example_words": ["bone", "home", "note"], "display_order": 3},
  {"symbol": "u_e", "category": "long_vowel", "example_words": ["cute", "mule", "tube"], "display_order": 4},
  {"symbol": "ai", "category": "long_vowel", "example_words": ["rain", "tail", "wait"], "display_order": 5},
  {"symbol": "ee", "category": "long_vowel", "example_words": ["tree", "bee", "see"], "display_order": 6},
  {"symbol": "oa", "category": "long_vowel", "example_words": ["boat", "coat", "road"], "display_order": 7},
  {"symbol": "oo", "category": "long_vowel", "example_words": ["moon", "food", "pool"], "display_order": 8},
  {"symbol": "ie", "category": "long_vowel", "example_words": ["pie", "tie", "lie"], "display_order": 9},

  {"symbol": "ar", "category": "r_controlled", "example_words": ["car", "star", "jar"], "display_order": 1},
  {"symbol": "er", "category": "r_controlled", "example_words": ["her", "after", "water"], "display_order": 2},
  {"symbol": "ir", "category": "r_controlled", "example_words": ["bird", "girl", "sir"], "display_order": 3},
  {"symbol": "or", "category": "r_controlled", "example_words": ["for", "horn", "corn"], "display_order": 4},
  {"symbol": "ur", "category": "r_controlled", "example_words": ["fur", "burn", "turn"], "display_order": 5},

  {"symbol": "oi", "category": "diphthong", "example_words": ["oil", "coin", "boil"], "display_order": 1},
  {"symbol": "oy", "category": "diphthong", "example_words": ["boy", "toy", "joy"], "display_order": 2},
  {"symbol": "ou", "category": "diphthong", "example_words": ["out", "cloud", "house"], "display_order": 3},
  {"symbol": "ow", "category": "diphthong", "example_words": ["cow", "how", "now"], "display_order": 4}
]
```

### Expected Counts by Category

| Category | Count |
|----------|-------|
| single_letter | 24 (19 consonants + 5 short vowels) |
| digraph | 8 |
| blend | 9 (6 initial + 3 final; `st` dual-role counted once) |
| long_vowel | 9 (4 magic-e + 5 vowel teams) |
| r_controlled | 5 |
| diphthong | 4 |
| **Total** | **59** |

### Data Migration

**File: `apps/phonics/migrations/0002_seed_phonemes.py`**

```python
import json
from pathlib import Path
from django.db import migrations


def seed_phonemes(apps, schema_editor):
    Phoneme = apps.get_model("phonics", "Phoneme")
    data_file = Path(__file__).resolve().parent.parent / "data" / "phonemes.json"
    with open(data_file, "r") as f:
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
```

### Idempotency

- Uses `update_or_create` with `symbol` as the lookup key
- Running `migrate` multiple times does not create duplicates
- Updates existing records if data changes in the JSON file
- `reverse_seed` provides rollback capability

## Acceptance Criteria

- [ ] All 59 phonemes seeded across 6 categories
- [ ] Each phoneme has ≥ 2 example words
- [ ] `manage.py migrate` applies seed without error
- [ ] Re-running migration does not create duplicates
- [ ] Specific phonemes verifiable: `sh`, `ch`, `a_e`, `ar`, `oi`

## Test Strategy

**File: `apps/phonics/tests/test_seed_data.py`**

```python
import pytest
from apps.phonics.models import Phoneme, PhonemeCategory


@pytest.mark.django_db
class TestPhonimeSeedData:
    def test_total_phoneme_count(self):
        assert Phoneme.objects.count() == 59

    def test_single_letter_count(self):
        assert Phoneme.objects.filter(category=PhonemeCategory.SINGLE_LETTER).count() == 24

    def test_digraph_count(self):
        assert Phoneme.objects.filter(category=PhonemeCategory.DIGRAPH).count() == 8

    def test_blend_count(self):
        assert Phoneme.objects.filter(category=PhonemeCategory.BLEND).count() == 9

    def test_long_vowel_count(self):
        assert Phoneme.objects.filter(category=PhonemeCategory.LONG_VOWEL).count() == 9

    def test_r_controlled_count(self):
        assert Phoneme.objects.filter(category=PhonemeCategory.R_CONTROLLED).count() == 5

    def test_diphthong_count(self):
        assert Phoneme.objects.filter(category=PhonemeCategory.DIPHTHONG).count() == 4

    def test_specific_phonemes_exist(self):
        for symbol in ["sh", "ch", "a_e", "ar", "oi"]:
            assert Phoneme.objects.filter(symbol=symbol).exists()

    def test_all_have_example_words(self):
        for p in Phoneme.objects.all():
            assert len(p.example_words) >= 2, f"{p.symbol} has < 2 example words"
```
