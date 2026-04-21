# Bug 2026_04_21_002 — Blend Builder Drag and Drop Does Not Work on Mobile

## Description

In the Blend Builder game (`/games/blend_builder/`), letter tiles cannot be dragged and dropped into word slots on mobile devices. The game uses the HTML5 Drag and Drop API, which is not supported on mobile touch browsers (iOS Safari, Android Chrome). This makes the core game mechanic non-functional on phones and tablets.

## Steps to Reproduce

1. Open the app on a mobile device (or use browser DevTools in touch-emulation / mobile mode).
2. Navigate to any Blend Builder game (e.g., via Games → Blend Builder).
3. Try to drag a letter tile from the letter bank into a word slot.

## Expected Behavior

Letter tiles should be draggable from the bank into the word slots using a touch drag gesture, just like they can be dragged with a mouse on desktop.

## Actual Behavior

Touch-dragging a letter tile does nothing — the browser may scroll the page or show a text-selection handle instead. The `dragstart`, `dragover`, and `drop` events never fire because mobile browsers do not support the HTML5 Drag and Drop API for touch input.

A click/tap fallback exists in the code (tap a tile to select it, then tap a slot to place it), but:

- The instruction text says "Drag the letters to spell the word!" which is misleading.
- The tap-to-select interaction is not discoverable — there is no visual affordance indicating tiles can be tapped to select first.

## Fix

Add touch event support to `static/js/games/blend_builder.js` so that drag-and-drop works on mobile:

1. **Add `touchstart`, `touchmove`, and `touchend`** event listeners to each `.letter-tile`:
   - On `touchstart`: record the tile being dragged and create a visual clone that follows the finger.
   - On `touchmove`: update the clone position using `e.touches[0].clientX/clientY`; use `document.elementFromPoint()` to detect which `.drop-slot` the finger is over and highlight it.
   - On `touchend`: determine the target slot via `document.elementFromPoint()` and call `placeTile()` if the finger ended over a valid slot; remove the clone.
   - Call `e.preventDefault()` in `touchmove` to prevent page scrolling while dragging.

2. **Update the instruction text** to be touch-friendly, e.g., "Drag or tap the letters to spell the word!"

3. **Apply `touch-action: none`** CSS to `.letter-tile` elements to prevent the browser from intercepting touch gestures for scrolling during a drag.
