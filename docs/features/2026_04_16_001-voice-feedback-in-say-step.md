# Feature: Voice Out Feedback in Say Step

## Description

In the learning flow (Listen → See → Say), after the child records their speech attempt in the Say (repeat) step, feedback is currently displayed as text on screen (e.g., "Great job!" or "Try rounding your lips more"). Young children who are learning phonics are often pre-readers or early readers and cannot interpret written feedback. Voicing the feedback aloud using text-to-speech makes the app accessible and effective for its target audience.

## Requirements

1. After a speech attempt response is received, the feedback text must be spoken aloud automatically using the existing TTS service.
2. The text feedback must still be displayed on screen alongside the audio (for parents/teachers observing).
3. Audio playback must not overlap with other app audio (e.g., phoneme playback).
4. If TTS fails (service unavailable), the app must degrade gracefully — show text feedback only, no error shown to the child.
5. The TTS voice should match the existing voice used elsewhere in the app (`en-US-AnaNeural`).
6. Feedback audio should be cached by the browser to avoid redundant TTS calls for repeated feedback phrases.

## Solution Options

### Option A: Client-side fetch from existing TTS endpoint

Call `GET /api/speech/tts/?text=<feedback>` from JavaScript after receiving the speech attempt response, then play the returned MP3 audio via an `<audio>` element or `AudioContext`.

**Pros:**

- TTS endpoint and service already exist and are fully implemented.
- Minimal backend changes — no new endpoints or logic needed.
- Browser caching via `Cache-Control: public, max-age=3600` (already set on the TTS endpoint).
- Simple JavaScript change (~10-15 lines in `speech.js`).

**Cons:**

- Extra HTTP round-trip after the speech attempt response (slight delay before audio plays).
- Feedback text must be URL-encoded and is limited to 100 characters (existing endpoint constraint).

### Option B: Return TTS audio inline with speech attempt response

Modify the `/api/speech/attempt/` endpoint to call `synthesize_speech()` server-side and return the audio data (base64-encoded) alongside the JSON response.

**Pros:**

- Single round-trip — feedback audio arrives with the response.
- No additional client-side fetch.

**Cons:**

- Increases response payload size significantly (MP3 audio blob in JSON).
- Couples STT processing with TTS generation — if TTS is slow, it delays the entire response.
- Requires changes to both the serializer and the view logic.
- Harder to cache individual feedback phrases.

### Option C: Browser-native Web Speech API (SpeechSynthesis)

Use the browser's built-in `window.speechSynthesis` API to speak the feedback text client-side, with no server call.

**Pros:**

- Zero server cost — no Azure TTS calls for feedback.
- No latency — speech starts immediately.
- No backend changes needed.

**Cons:**

- Voice quality and consistency varies across browsers and devices.
- Voice does not match the Azure `en-US-AnaNeural` voice used elsewhere in the app, creating an inconsistent experience.
- Limited control over pronunciation, speed, and intonation.
- Some mobile browsers have restrictions on `speechSynthesis` without user gesture.

## Recommended Solution

**Option A: Client-side fetch from existing TTS endpoint.**

This is the lowest-effort, lowest-risk approach. The TTS endpoint is already built, tested, and returns cached MP3 audio. The change is entirely in `static/js/speech.js` — after `showFeedback(data)` renders the text, fetch the audio from `/api/speech/tts/?text=<feedback>` and play it. The slight delay from the extra round-trip is acceptable since the text feedback appears instantly while the audio loads.

### Implementation Sketch

```javascript
// In showFeedback(), after setting feedbackText:
async function playFeedbackAudio(text) {
  try {
    const response = await fetch(
      `/api/speech/tts/?text=${encodeURIComponent(text)}`,
    );
    if (!response.ok) return; // Degrade gracefully
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    audio.play();
  } catch (e) {
    // TTS unavailable — text feedback is already shown
  }
}
```

## Implementation Notes

### Feedback Length Limit

The TTS endpoint has a 100-character limit on the `text` parameter. To ensure feedback always fits within this constraint, feedback was limited to <10 words via two layers:

1. **System prompt** (`apps/ai_tutor/data/default_prompts.json`): Updated instruction from "1-2 short sentences" to "1 short sentence of NO MORE THAN 10 words".
2. **Validator safety net** (`apps/ai_tutor/validators.py`): Added `MAX_WORDS = 10` — if the LLM exceeds 10 words, the validator truncates and adds punctuation.

### Browser Autoplay Policy

Modern browsers block `audio.play()` unless it occurs within a user gesture context. The mic button click starts the recording, but by the time the STT response and TTS fetch complete, the gesture context has expired.

**Attempted approaches:**

1. ~~Pre-create `Audio` element at click time, set `src` later~~ — Did not work. Browsers require `.play()` itself during a gesture, not just element creation.
2. ~~Use `AudioContext.decodeAudioData()` with pre-unlocked context~~ — Did not work. `decodeAudioData()` silently failed on MP3 format.
3. **Working fix:** Create an `AudioContext` and call `resume()` during the mic button click (user gesture). This unlocks audio playback for the entire page. Later, `playFeedbackAudio()` creates a standard `Audio` element with a blob URL from the TTS response and calls `.play()` — which succeeds because audio was already unlocked by the `AudioContext.resume()` call.

### TTS-Friendly Feedback Text

The AI tutor was generating feedback containing phonetic notation (e.g., "/b/", "/sh/") which the TTS service cannot pronounce. The system prompt was updated to instruct the LLM to never use phonetic symbols and instead use plain words (e.g., "the b sound" instead of "/b/").
