# Feature 2026_04_16_004: Thinking Animation for Say Step

## Description

On the Say step (`/learn/<symbol>/repeat/`), after a child records their voice the page shows plain text **"Thinking..."** while waiting for the LLM feedback response. Young children may not read or notice this small text, leading to confusion about whether the app is working. Replacing it with a visible, animated visual indicator will make the waiting state obvious and engaging for pre-readers.

## Requirements

1. Replace the "Thinking..." text with an animated visual element that is immediately noticeable to young children (ages 4–7).
2. The animation should convey "processing / working on it" without requiring reading ability.
3. The animation must be lightweight — no external libraries or large asset downloads.
4. The animation should disappear when feedback (stars + text) appears, matching the current flow.
5. The existing mascot (owl SVG in `static/images/mascot/mascot.svg`) should be leveraged if possible for visual consistency.

## Solution Options

### Option A: Animated Thinking Emoji Overlay

Replace `instruction.textContent = "Thinking..."` with a large animated emoji (e.g., 🤔 or 💭) using the existing `scale-in` keyframe from `animations.css`, plus a gentle bounce or pulse loop.

```html
<div class="thinking-animation">
  <span class="thinking-emoji">🤔</span>
  <span class="thinking-dots">...</span>
</div>
```

**Pros:**

- Zero new assets — uses built-in emoji glyphs
- Trivial to implement — a few lines of CSS + one JS change
- Emoji are universally recognizable to young children

**Cons:**

- Emoji rendering varies by OS/device
- Less branded / less visually distinctive than the mascot

### Option B: Mascot with Thinking Speech Bubble

Show the existing owl mascot SVG with a CSS-animated speech bubble containing bouncing dots (the classic "typing indicator" pattern).

```html
<div class="thinking-animation">
  <img src="/static/images/mascot/mascot.svg" class="thinking-mascot" alt="" />
  <div class="thinking-bubble">
    <span class="dot"></span><span class="dot"></span><span class="dot"></span>
  </div>
</div>
```

**Pros:**

- Reuses the existing mascot for visual consistency across the app
- Bouncing dots are a well-known "thinking" pattern
- Fully CSS-animated — no JS animation libraries

**Cons:**

- Slightly more CSS to write (bubble shape + dot animation)
- Mascot is currently a simple circle owl — may look small in the center of the page

### Option C: Full-screen Lottie / GIF Animation

Add a pre-made animated GIF or Lottie JSON of a thinking character.

**Pros:**

- Could be very polished and visually appealing

**Cons:**

- Requires sourcing/licensing an animation asset
- Adds significant page weight (Lottie player ~50KB + animation JSON)
- External dependency for a single loading state is overkill

## Recommended Solution

**Option B: Mascot with thinking speech bubble.**

The owl mascot is already part of the app's visual identity. Showing it with bouncing dots creates an instantly recognizable "I'm thinking" state without requiring reading. The implementation is pure CSS — no new dependencies — and the bouncing-dots pattern is widely understood even by pre-readers.

Implementation steps:

1. Add a hidden `#thinkingAnimation` div to `templates/learning/repeat.html` containing the mascot image and a speech bubble with 3 dots.
2. Add `.thinking-animation`, `.thinking-bubble`, and `.thinking-dot` styles with a staggered bounce animation to `static/css/learning.css`.
3. In `static/js/speech.js`, show `#thinkingAnimation` alongside the existing "Thinking..." instruction text when feedback is loading, and hide the animation when feedback arrives. The text is kept for parents who may be reading the screen.
