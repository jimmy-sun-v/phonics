# BUG 2026_04_16_006: Previous Feedback Persists on Re-record

## Description

On the Say step (`/phonics/learn/<symbol>/repeat/`), when a user clicks the microphone button to record a second attempt, the star rating and feedback text from the previous attempt remain visible during and after the new recording. This is confusing because the old result overlaps with the new "Thinking..." state and may mislead users into thinking no new evaluation occurred.

## Steps to Reproduce

1. Navigate to `/phonics/learn/b/repeat/`
2. Click the microphone button and say the word
3. Observe the star rating and feedback text appear
4. Click the microphone button again to re-record
5. Observe the previous stars and feedback are still visible while recording and during "Thinking..."

## Expected Behavior

When the user clicks the microphone to record again, the previous feedback (stars, feedback text, and navigation buttons) should be hidden immediately. New feedback should only appear once the new response is received.

## Actual Behavior

The previous stars, feedback text, and navigation buttons remain visible during the second recording and processing, creating visual confusion.

## Fix

**File:** `static/js/speech.js`

Added two lines at the start of `startRecording()` to hide the feedback area and step navigation before beginning a new recording:

```js
feedbackArea.style.display = "none";
stepNav.style.display = "none";
```

This mirrors the logic already in `resetForRetry()` but triggers automatically when the user taps the mic button instead of requiring them to click "Try Again" first.
