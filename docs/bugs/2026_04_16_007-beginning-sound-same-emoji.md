# BUG 2026_04_16_007: Beginning Sound Game Shows Same Emoji for All Words

## Description

In the Beginning Sound game, the target word area displays a hardcoded 🖼️ emoji regardless of the word being shown. This makes the game less engaging and harder for pre-readers who rely on visual cues to identify the word.

## Steps to Reproduce

1. Navigate to `/phonics/learn/b/practice/`
2. Click "Beginning Sound"
3. Observe the target word area — it shows 🖼️ next to the word "bat"
4. Navigate to another phoneme's Beginning Sound game (e.g., `/games/beginning_sound/c/`)
5. Observe — it still shows 🖼️ next to "cat"

## Expected Behavior

Each target word should display a word-specific emoji (e.g., 🦇 for "bat", 🐱 for "cat") to help children visually identify the word.

## Actual Behavior

All words display the same generic 🖼️ emoji.

## Fix

**Files:** `apps/games/page_views.py`, `templates/games/beginning_sound.html`

1. In `beginning_sound_view()`, added an `example_emoji` context variable using the existing `WORD_EMOJI` lookup dictionary (already used by the Sound Picture game):

   ```python
   example_emoji = WORD_EMOJI.get(example_word, DEFAULT_EMOJI)
   ```

2. In the template, replaced the hardcoded `🖼️` with `{{ example_emoji }}` to render the word-specific emoji.
