# Bug 2026_04_16_008 — Speech Assessment Uses Wrong Azure API

## Description

The speech assessment feature uses the standard Azure **Speech-to-Text** (`SpeechRecognizer.recognize_once()`) API instead of the dedicated **Pronunciation Assessment** API. The confidence score returned by STT measures how confident Azure is that it transcribed the audio correctly — not how accurately the user pronounced the target phoneme. This means a user can say a completely unrelated sentence clearly and still receive a high confidence score (e.g. 0.95), making the pronunciation feedback unreliable.

## Steps to Reproduce

1. Start a phonics learning session for any phoneme (e.g. "sh").
2. Instead of saying the target phoneme or word, say a completely different sentence clearly (e.g. "I like pizza").
3. Observe the confidence score and feedback returned.

## Expected Behavior

- The system should detect that the user did not produce the expected phoneme/word.
- The confidence/accuracy score should be low because the spoken content does not match the reference text.
- The user should receive corrective feedback prompting them to try the target sound again.

## Actual Behavior

- Azure STT transcribes the unrelated sentence with high confidence (e.g. 0.95) because it was spoken clearly.
- The `error_detection.detect_error()` function may still flag a mismatch based on text comparison, but the confidence score itself is misleadingly high and is passed through to the LLM feedback prompt and stored in attempt records.
- The `expected_text` parameter accepted by `recognize_speech()` in `apps/speech/azure_client.py` (line 23) is never used in the function body.

## Fix

Replaced the standard `SpeechRecognizer` with Azure's **Pronunciation Assessment** API (`PronunciationAssessmentConfig`). The `PronunciationScore` (0–100 scale) is now used as the single consolidated confidence metric, mapped to the existing 3-star feedback system.

### Changes Applied

**`apps/speech/azure_client.py`**

- Added `PronunciationAssessmentConfig` with `reference_text`, `HundredMark` grading, and `Phoneme` granularity.
- Config is applied to the recognizer via `pronunciation_config.apply_to(recognizer)` when `expected_text` is provided.
- Added `_extract_pronunciation_score()` to extract `PronScore` from `NBest[0].PronunciationAssessment`.
- Falls back to standard STT confidence when no `expected_text` is given.

**`apps/speech/views.py`**

- Looks up the `Phoneme` object and passes its first `example_word` (e.g. `"bat"`, `"ship"`) as `expected_text` to `recognize_speech()`, matching what the UI instructs the child to say. Previously passed the raw phoneme symbol (e.g. `"b"`), which caused scores to always be low because the spoken word didn't match the single-letter reference.
- Added import for `apps.phonics.models.Phoneme`.

**`apps/speech/error_detection.py`**- `LOW_CONFIDENCE_THRESHOLD` default updated from `0.5` to `50` (0–100 scale).

**`apps/speech/models.py`**

- `confidence` field validator updated from `MaxValueValidator(1.0)` to `MaxValueValidator(100.0)`.
- Help text updated to "Pronunciation assessment score (0-100)".

**`config/settings/base.py`**

- `PHONEME_COMPLETION_THRESHOLD` updated from `0.7` to `70`.
- `LOW_CONFIDENCE_THRESHOLD` updated from `0.5` to `50`.

**`apps/ai_tutor/feedback.py`**

- Encourage threshold updated from `0.6` to `60`.

**`static/js/speech.js`**

- Star rating thresholds updated: `>= 80 → 3 stars`, `>= 50 → 2 stars`, `< 50 → 1 star`.

**Tests updated** across `test_error_detection.py`, `test_models.py`, `test_feedback.py`, `test_ai_safety.py`, `test_diagnostics.py`, `test_purge.py`, `test_services.py`, `test_models.py` (ai_tutor), `test_prompt_rendering.py`, `test_seed_prompts.py`, and `test_progress.py` to use 0–100 scale values.

### LLM Feedback Not Matching Score

The LLM prompt template did not instruct the model to vary feedback tone based on the pronunciation score. Regardless of a low score, the LLM would still respond with praise like "Great try! You said the b sound really well!"

**`apps/ai_tutor/migrations/0004_update_feedback_prompt_v2.py`** (new)

- Created prompt template v2 with explicit score-to-tone mapping:
  - **80–100**: Celebrate success enthusiastically.
  - **50–79**: Encourage and gently guide.
  - **Below 50**: Be supportive and offer help, never praise accuracy.
- User template now presents the score as "Pronunciation score: {confidence} out of 100" and reinforces "only praise accuracy if the score is 80 or above."
- Deactivates v1 and creates v2 with inline content (not from the JSON seed file, to keep migration reproducibility).

**`apps/ai_tutor/data/default_prompts.json`**

- Preserved as v1 for migration 0002 reproducibility.

### Wrong Reference Text Causing Low Scores

After switching to Pronunciation Assessment, scores were always low because the `reference_text` passed to Azure was the raw phoneme symbol (e.g. `"b"`) while the UI instructs children to say the first example word (e.g. `"bat"`).

**`apps/speech/views.py`**

- Now looks up `Phoneme.objects.get(symbol=phoneme_symbol)` and uses `phoneme_obj.example_words[0]` as the reference text, matching what the child is asked to say.

### Score Consolidation

Azure Pronunciation Assessment returns multiple scores (AccuracyScore, FluencyScore, CompletenessScore, PronunciationScore). We use the composite **`PronunciationScore`** directly because:

- It is Azure's built-in weighted composite, suitable out of the box.
- `FluencyScore` penalizes hesitation, which is unfair for young children.
- `CompletenessScore` is less meaningful for single-phoneme exercises.
- `AccuracyScore` alone is too narrow.

### Reference

[Azure Pronunciation Assessment documentation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/how-to-pronunciation-assessment)
