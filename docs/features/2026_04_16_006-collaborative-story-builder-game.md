# Feature 2026_04_16_006 — Collaborative Story Builder Game

## Description

A new game where kids and the LLM take turns building a story together. The child starts with an opening sentence (spoken via microphone), the LLM continues with the next part, and they alternate for 3–4 rounds. This exercises the child's imagination, oral expression, and listening skills in a playful, low-pressure format.

Key benefits:

- **Creative expression**: Children practice forming sentences and telling stories.
- **Active listening**: Children must listen to the LLM's continuation before adding their own.
- **Vocabulary exposure**: The LLM models age-appropriate language in its story segments.
- **Engagement**: Turn-taking with an AI co-author feels collaborative, not evaluative — no scores, no "wrong" answers.

## Requirements

### Functional

1. **Turn-based flow**: The game alternates between child (speech input) and LLM (text + TTS output) turns for a fixed number of rounds (3–4 configurable).
2. **Child input via speech**: The child taps a mic button to record their story segment. The recording is sent to Azure STT for transcription (standard speech-to-text, not pronunciation assessment). The transcribed text is displayed on screen.
3. **LLM continuation**: After each child turn, the LLM generates a 1–2 sentence continuation that:
   - Is age-appropriate (5–7 year olds).
   - Naturally follows from the child's contribution.
   - Gently invites (but does not pressure) the child to continue (e.g. "What do you think happened next?").
   - On the final LLM turn, wraps up the story with a summary.
4. **TTS playback**: Every LLM response is read aloud via TTS automatically.
5. **Repeat last**: A "Say it again" button lets the child replay the LLM's most recent response via TTS.
6. **Repeat whole story**: A "Hear the whole story" button replays the entire story so far (all turns concatenated) via TTS.
7. **Story summary**: After the final round, the LLM produces a child-friendly summary of the complete story and reads it aloud.
8. **No scoring**: This is a creative exercise — no stars, no confidence scores, no pass/fail.
9. **Visual story trail**: Each turn is displayed as a chat-like bubble (child on one side, LLM on the other) so the child can see the story growing.
10. **Session tracking**: Story sessions are linked to the existing `LearningSession` for activity logging, but no `SpeechAttempt` records are created.
11. **Intro read aloud**: When the game starts, the introductory explanation text is read aloud via TTS so early readers don't need to read it themselves.
12. **Think-before-talk prompt**: Instruction text encourages the child to think about what they want to say before tapping the mic, to reduce wasted STT/TTS processing on accidental or empty recordings.
13. **Recording timer bar**: A visual countdown bar (default 30 seconds) is displayed while the child is recording, so they know how much time they have. The bar turns red in the last 5 seconds, and recording auto-stops when time runs out.

### Non-functional

- Round limit is server-configurable via Django settings (`STORY_BUILDER_MAX_ROUNDS`, default 4).
- LLM calls use the existing `call_llm()` infrastructure with a new `PromptTemplate` named `story_builder`.
- TTS reuses the existing `/api/speech/tts/` endpoint (supports up to 10,000 characters per call). For "whole story" replay, the client concatenates all segments into a single TTS call.
- The game should be accessible from the games menu and optionally linked from a phoneme's practice flow.

### Safety

- The LLM system prompt must include the same child-safety rules as the phonics feedback template (no personal questions, no negative language, no open-ended questions beyond story continuation).
- The `validate_response()` function from `apps.ai_tutor.validators` should be applied to LLM story segments, but with a relaxed length limit (2 sentences / 30 words instead of 10 words) since story segments are naturally longer.
- If the child's transcribed speech contains inappropriate content, the LLM should gently redirect without acknowledging the inappropriate content.

## Solution Options

### Option A: Standalone API endpoint + new template page

Add a new API endpoint `POST /api/games/story/turn/` that accepts `{session_id, text}` and returns `{llm_response, round_number, is_final, summary}`. The frontend is a new Django template at `/games/story_builder/` with vanilla JS managing the turn state client-side.

**Pros:**

- Follows the existing architectural pattern (REST API + server-rendered template + vanilla JS).
- All LLM interaction stays server-side behind an API.
- Client is stateless — the server tracks round number and story context.

**Cons:**

- The full story context must be sent to the LLM on each turn (messages array grows), requiring the server to store or reconstruct conversation history.
- Needs a new model or session storage for the story state.

### Option B: WebSocket-based real-time conversation

Use Django Channels to create a WebSocket endpoint for the story conversation, enabling real-time streaming of LLM responses.

**Pros:**

- LLM responses can stream token-by-token for a more interactive feel.
- Naturally maintains conversation state in the WebSocket connection.

**Cons:**

- Introduces a new infrastructure dependency (Django Channels, Redis/in-memory channel layer).
- Significantly more complex than the existing REST-only architecture.
- Over-engineered for 3–4 turn exchanges with short responses.

### Option C: Client-side conversation state with stateless API

The frontend maintains the full conversation history in JS and sends the complete message array on each turn to a thin API endpoint `POST /api/games/story/turn/` that simply forwards to `call_llm()` and returns the response.

**Pros:**

- Simplest server-side implementation — no new models or session storage needed.
- Follows existing patterns (client JS drives the experience).
- Easy to implement "repeat whole story" since the client already has all segments.

**Cons:**

- Full conversation context is sent over the wire each turn (minimal concern for 3–4 rounds of short text).
- Client must be trusted with conversation state (acceptable since there's no scoring).

## Recommended Solution

**Option A: Standalone API endpoint + new template page**, with a lightweight server-side story state.

Justification:

1. **Consistency**: All existing games use the REST API + template pattern. No new infrastructure.
2. **Server-side state**: Storing story turns in a simple `StorySession` model (or reusing the existing session with a JSON field) keeps the LLM conversation context server-side, which is safer and enables "repeat whole story" without trusting the client.
3. **Scalability**: If we later want to save/share completed stories or add a "story library" feature, having the data server-side is essential.
4. **Simplicity over Option B**: WebSockets are unnecessary for 3–4 synchronous turn exchanges.
5. **Safety over Option C**: Server-side state means we can validate and sanitize the conversation history before each LLM call, and the client can't tamper with previous turns.

### Recommended implementation outline

**New model**: `StorySession` in `apps/games/models.py`

```python
class StorySession(models.Model):
    session = models.ForeignKey("learning_sessions.LearningSession", on_delete=models.CASCADE)
    turns = models.JSONField(default=list)  # [{role: "child"|"llm", text: "..."}]
    max_rounds = models.PositiveIntegerField(default=4)
    is_complete = models.BooleanField(default=False)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**New API endpoint**: `POST /api/games/story/turn/`

- Input: `{session_id, story_session_id (optional, for continuing), text}`
- On first call (no `story_session_id`): creates `StorySession`, saves child's opening, calls LLM for continuation.
- On subsequent calls: appends child turn, calls LLM. If final round, requests summary.
- Output: `{story_session_id, llm_response, round_number, total_rounds, is_complete, summary}`

**New prompt template**: `story_builder` (seeded via migration)

- System prompt defines the co-storytelling role, child safety rules, turn behavior, and summary instructions.
- User template passes the full conversation history so the LLM has context.

**New template**: `templates/games/story_builder.html`

- Chat-bubble UI showing alternating turns.
- Mic button for child input (reuses recording logic from `speech.js`).
- "Say it again" button — calls `/api/speech/tts/` with the last LLM response.
- "Hear the whole story" button — concatenates all turns and plays via a single TTS call.
- "Finish" state showing the summary with a celebration animation.

**New JS**: `static/js/games/story_builder.js`

- Manages recording, API calls, turn display, and TTS playback.
- Disables mic during LLM/TTS turns to enforce turn-taking.

**New page URL**: `/games/story_builder/` (no phoneme symbol needed — this game is phoneme-independent).
