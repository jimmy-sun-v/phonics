# Feature 2026_04_16_003: Seed Practice Step Games

## Description

The practice step in the learning flow (`/phonics/learn/<symbol>/practice/`) shows "No games for this sound yet" for every phoneme. Four game types are fully implemented in code (views, templates, JavaScript) but no `Game` or `GamePhonemeMapping` records exist in the database, so games never appear. This feature seeds game data so children can play games during the practice step.

## Requirements

1. Games must appear on the practice step for every phoneme.
2. Game selection should be age-appropriate — only easy games for young learners.
3. Game data must be seeded automatically via a Django data migration (no manual admin setup).
4. The seed data must follow the same pattern as `apps/phonics/migrations/0002_seed_phonemes.py` — load from a JSON file, be idempotent (`update_or_create`), and include a reverse migration.
5. All 60 phonemes across 6 categories (single_letter, digraph, blend, long_vowel, r_controlled, diphthong) must have at least 2 games available.
6. Games that are too complex for a given phoneme category should be excluded (e.g., Blend Builder requires short, spellable words).

## Existing Game Types (already implemented)

| Game Type         | Mechanic                                             | Difficulty | Best For                           |
| ----------------- | ---------------------------------------------------- | ---------- | ---------------------------------- |
| `sound_picture`   | Hear a sound, tap the matching picture               | Easy       | All phonemes — pure recognition    |
| `beginning_sound` | See a word, pick which letter/digraph it starts with | Easy       | Single letters, digraphs           |
| `balloon_pop`     | Pop floating balloons labelled with the target sound | Easy       | All phonemes — motor + recognition |
| `blend_builder`   | Drag letters to spell the example word               | Medium     | Short words only (3–4 letters)     |

## Solution Options

### Option A: Seed all 4 existing games for all phonemes

Create a data migration that inserts 4 `Game` records (one per type) and maps each to all 60 phonemes via `GamePhonemeMapping`.

**Pros:**

- Zero new code — all views, templates, and JS already exist and are tested.
- Every phoneme gets the maximum variety of games.
- Single migration file + JSON data file.

**Cons:**

- Blend Builder may be too hard for complex phonemes (e.g., spelling "umbrella" for `u`, or "phone" for `ph` — silent letters make it confusing).
- Beginning Sound doesn't make sense for non-initial phonemes (e.g., `ng` — "ring" doesn't _start_ with `ng`).

### Option B: Seed games selectively by category

Create 4 `Game` records but map them to phonemes based on suitability:

| Game Type         | Mapped Categories                                              |
| ----------------- | -------------------------------------------------------------- |
| `sound_picture`   | All 6 categories                                               |
| `balloon_pop`     | All 6 categories                                               |
| `beginning_sound` | `single_letter`, `digraph` (sounds that appear word-initially) |
| `blend_builder`   | `single_letter`, `blend` (short, phonetically regular words)   |

**Pros:**

- Every phoneme gets at least 2 easy games (Sound Picture + Balloon Pop).
- Avoids confusing mismatches (e.g., "spell 'umbrella'" or "what sound does 'ring' start with?").
- Still zero new code — only data.

**Cons:**

- Some phonemes get only 2 games instead of 4.
- Mapping logic adds complexity to the seed data / migration.

### Option C: Create new ultra-simple game types + seed data

Add 1–2 new game types designed to be simpler than the existing four:

- **Odd One Out**: Show 4 words/pictures — 3 contain the target sound, 1 doesn't. Tap the odd one.
- **Sound or Not**: Hear a word, tap 👍 if it contains the target sound or 👎 if it doesn't. Repeat 5 times.

Then seed these alongside the existing games.

**Pros:**

- Even lower cognitive load than existing games.
- Fresh variety for kids who replay sounds.

**Cons:**

- Requires new views, templates, JS, and model changes (new `GameType` choices).
- Significantly more implementation work for incremental value — the existing games are already quite easy.

## Recommended Solution

**Option B: Seed games selectively by category.**

The four existing games are already fully implemented and span a good range of easy mechanics (tapping, popping, matching, spelling). Seeding them selectively avoids inappropriate pairings while still giving every phoneme at least 2 games. This requires only a JSON data file and a data migration — no new code.

Implementation steps:

1. Create `apps/games/data/games_seed.json` with 4 game records.
2. Create `apps/games/data/game_phoneme_mappings.json` with category-based mapping rules.
3. Create migration `apps/games/migrations/0002_seed_games.py` that loads the JSON, creates the `Game` records, and builds `GamePhonemeMapping` records by querying phonemes per category.
4. Run `python manage.py migrate` to populate the database.
