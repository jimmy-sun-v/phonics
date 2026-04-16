# BUG 2026_04_16_005: Games Missing Completion Flow and Distinct Visuals

## Description

Two issues with the practice step games:

1. **No game completion flow** — Beginning Sound, Sound Picture, and Blend Builder games had no "game complete" overlay or way to return to the practice step after finishing. Players were stuck on the game page. Only Balloon Pop had a completion overlay with a "Continue" button.

2. **Sound Picture shows identical images** — All four picture cards displayed the same generic 🖼️ emoji. The view generated `image_path` values pointing to `images/phonemes/*.png`, but no such images exist and the template never used the path — it hardcoded 🖼️ for every card.

## Steps to Reproduce

### Issue 1 — No completion flow

1. Navigate to `/phonics/learn/b/practice/`
2. Click "Beginning Sound"
3. Pick the correct letter → score updates but nothing else happens
4. No way to go back to the practice step

### Issue 2 — Identical images

1. Navigate to `/phonics/learn/b/practice/`
2. Click "Sound → Picture"
3. All 4 cards show the same 🖼️ emoji — only the word label differs

## Expected Behavior

1. After completing a game, a "Great job!" overlay should appear with a "Continue" button that returns to the practice step.
2. Each picture card should show a distinct visual representing its word.

## Actual Behavior

1. Games end silently — no overlay, no navigation back.
2. All cards show 🖼️.

## Fix

### Issue 1 — Game completion overlay

Added `showGameComplete()` to three game JS files, matching Balloon Pop's existing pattern:

- **`static/js/games/beginning_sound.js`** — overlay after picking the correct letter
- **`static/js/games/sound_picture.js`** — overlay after tapping the correct picture
- **`static/js/games/blend_builder.js`** — overlay after spelling the word correctly

Each overlay uses `history.back()` for the "Continue" button, returning the player to the practice step.

### Issue 2 — Word-specific emojis

- **`apps/games/page_views.py`** — Added a `WORD_EMOJI` dictionary mapping all example words from `phonemes.json` to appropriate emojis (e.g., `cat` → 🐱, `sun` → ☀️, `tree` → 🌳). Replaced `image_path` with `emoji` in the options context. Unknown words fall back to 🖼️.
- **`templates/games/sound_picture.html`** — Changed `🖼️` to `{{ option.emoji }}` so each card shows its word's emoji.
