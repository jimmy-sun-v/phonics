# BUG 2026_04_16_002: TTS Voice Speed Not Configurable via SSML Prosody

## Description

The text-to-speech service uses SSML with `<prosody rate="slow">` to control speech speed, but changing the `rate` attribute has no audible effect on the output. The voice always plays at the same speed regardless of the SSML prosody settings. This prevents tuning the speech speed for young children (5–7), who benefit from slower, clearer pronunciation.

## Steps to Reproduce

1. Start the dev server: `python manage.py runserver`
2. Call the TTS endpoint: `GET /api/speech/tts/?text=Hello+there`
3. Note the speech speed
4. In `apps/speech/tts_service.py`, change `_build_ssml()` prosody rate from `"slow"` to `"x-slow"` or `"fast"`
5. Restart the server and call the same endpoint
6. Compare — the speech speed is identical

## Expected Behavior

Changing the SSML `<prosody rate="...">` attribute should produce audibly different speech speeds (e.g., `"x-slow"` noticeably slower than `"fast"`).

## Actual Behavior

The speech speed remains unchanged regardless of the `rate` value in the SSML prosody element.

## Root Cause Analysis

The `speech_config.speech_synthesis_voice_name` was previously set on the SDK config object AND the voice was also specified in the SSML `<voice name="...">` element. This double configuration may cause the SDK to ignore SSML-level prosody attributes. However, removing `speech_synthesis_voice_name` from `speech_config` (so only SSML controls the voice) may not fully resolve the issue, as the root cause could be deeper.

## Possible Solutions

### 1. Remove `speech_synthesis_voice_name` from `speech_config` (already applied)

Let the SSML be the sole source of voice and prosody configuration. When `speech_config` also sets a voice, the SDK may treat the SSML voice/prosody as redundant.

**Status:** Applied but unconfirmed whether this fully resolves the issue.

### 2. Use percentage-based rate values instead of named values

Azure TTS may respond differently to explicit percentage values vs. named presets. Replace `rate="slow"` with an explicit percentage like `rate="-30%"` or `rate="70%"`.

```xml
<prosody rate="-30%" pitch="medium">
    Hello there
</prosody>
```

### 3. Use `speak_ssml_async` instead of `speak_ssml`

The synchronous `speak_ssml()` method may have edge cases where SSML attributes are not fully processed. Switching to the async API could resolve the issue:

```python
result_future = synthesizer.speak_ssml_async(ssml)
result = result_future.get()
```

### 4. Use `mstts:express-as` for style-based speed control

Azure Neural voices support the `mstts` namespace for style control, which may be more reliable than standard `<prosody>`:

```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
       xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-US">
    <voice name="en-US-AnaNeural">
        <mstts:express-as style="friendly">
            <prosody rate="slow">
                Hello there
            </prosody>
        </mstts:express-as>
    </voice>
</speak>
```

### 5. Verify with Azure Speech Studio

Test the SSML directly in [Azure Speech Studio](https://speech.microsoft.com/portal) to determine if the issue is with the SDK, the voice model (`en-US-AnaNeural`), or the SSML structure. If Speech Studio produces the correct speed, the issue is in the SDK usage. If not, it may be a voice model limitation.

### 6. Try a different voice

Some neural voices have limited prosody control. Test with an alternative child-friendly voice (e.g., `en-US-AnaNeural` → `en-US-JennyNeural` or `en-US-SaraNeural`) to determine if the issue is voice-specific.
