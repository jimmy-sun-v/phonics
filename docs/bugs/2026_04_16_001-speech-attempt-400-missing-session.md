# BUG-001: Speech Attempt API Returns 400 — Missing Session ID

## Description

The `/api/speech/attempt/` endpoint returns a `400 Bad Request` when triggered from the browser UI during the repeat step of the learning flow. The root cause is that no `LearningSession` is created during the learning flow, so `session_id` is passed as an empty string instead of a valid UUID, failing serializer validation.

## Steps to Reproduce

1. Start the development server: `python manage.py runserver`
2. Navigate to `http://127.0.0.1:8000/phonics/`
3. Select a category, then select a phoneme
4. Progress through the listen step to the repeat step
5. Record and submit a speech attempt

## Expected Behavior

The speech attempt is submitted with a valid `session_id` UUID, the API processes the audio, and returns a response with confidence score and feedback.

## Actual Behavior

The API returns `400 Bad Request` with validation errors. The server logs:

```
Bad Request: /api/speech/attempt/
"POST /api/speech/attempt/ HTTP/1.1" 400 40
```

The `SpeechAttemptRequestSerializer` rejects the request because `session_id` is an empty string (`""`) instead of a valid UUID.

## Fix

**File:** `apps/phonics/page_views.py`

The `listen_step_view` function — the first step in the learning flow — was not creating a `LearningSession`. The `repeat_step_view` downstream read `learning_session_id` from the Django session (`request.session`), but nothing ever set it.

**Changes applied:**

1. Imported `create_session` from `apps.sessions.services`
2. In `listen_step_view`, added a call to `create_session()` and stored the resulting `session_id` in `request.session["learning_session_id"]`

```python
def listen_step_view(request, symbol):
    phoneme = get_phoneme_detail(symbol)
    if phoneme is None:
        return redirect("phonics:category-list-page")

    session = create_session()
    request.session["learning_session_id"] = str(session.session_id)

    return render(request, "learning/listen.html", {"phoneme": phoneme})
```

---

## Follow-up Issue: STT Returns "No speech recognized"

### Issue

After the session fix, the speech attempt no longer returns 400, but Azure Speech-to-Text fails with "No speech recognized":

```
[2026-04-16 13:49:57,285] INFO phonics.requests attempt_request_start
[2026-04-16 13:49:59,756] INFO phonics.speech service_call
STT failed for session aa866745-7c8d-4a08-a11c-7639cc8cb5d7: No speech recognized
[2026-04-16 13:49:59,756] INFO phonics.requests attempt_request_end
```

### Root Cause Analysis

There is an **audio format mismatch** between the browser and Azure Speech SDK:

- **Browser** (`static/js/speech.js`): Records audio using `MediaRecorder` with `audio/webm;codecs=opus` — an Opus-encoded WebM container. The audio is base64-encoded and sent to the API.
- **Azure SDK** (`apps/speech/azure_client.py`): Uses `PushAudioInputStream` with no `AudioStreamFormat` specified, which defaults to **16-bit PCM, 16000 Hz, mono**. The raw WebM/Opus bytes are written directly to the stream.

The Azure SDK cannot decode Opus-encoded audio and silently returns "No speech recognized" instead of an explicit format error.

### Possible Solutions

1. **Server-side transcoding** — Convert WebM/Opus to PCM WAV on the server before passing to the Azure SDK (e.g., using `pydub` or `ffmpeg`). This is the most reliable approach since all browsers produce WebM/Opus.

2. **Specify audio format in Azure SDK** — If the SDK supports compressed audio input, configure `AudioStreamFormat` to accept Opus/WebM. The Azure Speech SDK does support compressed formats via `AudioStreamFormat.get_compressed_format()`.

3. **Browser-side WAV recording** — Use a library like `RecordRTC` or a custom `AudioWorklet` to capture audio as raw PCM/WAV in the browser, avoiding the format mismatch entirely. This avoids server-side dependencies but adds client-side complexity.

### Fix Applied

**Option 1 — Server-side transcoding** was chosen as the most reliable approach.

**Changes:**

- **`apps/speech/azure_client.py`** — Added `_convert_to_wav()` helper using `pydub.AudioSegment` to convert incoming WebM/Opus audio to 16-bit 16kHz mono PCM WAV before passing to the Azure SDK.
- **`requirements.txt`** — Added `pydub>=0.25`.
- **`scripts/check_tools.ps1`** — Added ffmpeg check since pydub depends on it.

### Deployment Consideration: ffmpeg on Azure App Service

`pydub` requires `ffmpeg` to be available on the system. This has deployment implications:

- **Azure App Service (Linux)**: The Python runtime images (`PYTHON|3.11`) **include ffmpeg by default** as part of the Debian-based container. No additional configuration is needed in the Bicep template or `startup.sh`.
- **Custom containers**: If the app is ever moved to a custom Docker image, `ffmpeg` must be explicitly installed (e.g., `apt-get install -y ffmpeg`).
- **Local development (Windows)**: `ffmpeg` must be installed manually (e.g., `winget install ffmpeg`) and added to `PATH`. This is now checked by `scripts/check_tools.ps1`.
