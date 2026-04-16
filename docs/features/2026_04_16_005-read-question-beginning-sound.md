# Feature 2026_04_16_005: Read Question Aloud in Beginning Sound Game

## Description

In the Beginning Sound game, the question ("What sound does it start with?") and the target word are displayed as text only. Young children who cannot read have no way to understand the question or identify the target word. The Sound Picture game already uses TTS to read the target word aloud on page load — the Beginning Sound game should do the same.

## Requirements

1. When the Beginning Sound game loads, the target example word must be read aloud using the existing TTS endpoint (`/api/speech/tts/`).
2. The question or word should play automatically on page load, matching the Sound Picture game's behavior.
3. A "Hear Word" button should be available so the child can replay the word at any time.
4. The implementation should reuse the existing TTS infrastructure — no new backend changes.

## Solution Options

### Option A: Add TTS to JS only

Add a `playTargetWord()` function to `beginning_sound.js` that fetches `/api/speech/tts/?text=<word>` and plays the audio. Call it on `DOMContentLoaded`. Read the word from the existing `.target-label` element in the DOM.

**Pros:**

- Minimal change — ~10 lines of JS
- No template or backend changes
- Consistent with how Sound Picture does it

**Cons:**

- No replay button — child can only hear it once on page load
- Autoplay may be blocked by browser on first visit (though the user will have interacted with the practice step before reaching this game)

### Option B: Add TTS to JS + "Hear Word" button in template

Same as Option A, but also add a "🔊 Hear Word" button to the template (matching Sound Picture's "🔊 Hear Sound" button). Wire it to replay the TTS audio.

**Pros:**

- Child can replay the word as many times as needed
- Consistent UI with Sound Picture's "Hear Sound" button
- Still minimal change — ~15 lines of JS + 1 button in template

**Cons:**

- Slightly more HTML, but trivially small

### Option C: Pre-generate audio files for all words

Store pre-recorded audio for each example word and serve them as static files rather than using runtime TTS.

**Pros:**

- No dependency on Azure TTS being available
- Faster playback (no network round-trip)

**Cons:**

- Requires generating and maintaining 60+ audio files
- Adds complexity for a problem already solved by the TTS endpoint
- Overkill when TTS is already used elsewhere in the app

## Recommended Solution

**Option B: Add TTS to JS + "Hear Word" button.**

This matches the Sound Picture game's UX pattern and gives children the ability to replay the word. The changes are minimal — one button in the template and a small JS function — and reuse the existing TTS endpoint.

Implementation steps:

1. Add a "🔊 Hear Word" button to `templates/games/beginning_sound.html` in the game header.
2. In `static/js/games/beginning_sound.js`, add a `playTargetWord()` function that fetches TTS for the word from `.target-label` and plays it. Call on page load and on button click.
