# Feature: Star Rating for Confidence Score

## Description

The speech attempt confidence score is currently displayed as a progress bar (`.confidence-bar` / `.confidence-fill`), which is not intuitive or rewarding for young children aged 5–7. Replace it with a **3-star rating system** that provides clear, motivating visual feedback. This change should apply everywhere the confidence bar is used, not just the repeat step.

## Requirements

1. Replace the progress bar with a 3-star rating display in all templates that use `.confidence-bar` / `.confidence-fill`.
2. Map confidence score to stars:

   | Confidence Range | Stars  | Visual  |
   | ---------------- | ------ | ------- |
   | 0.0 – 0.39       | ⭐☆☆   | 1 star  |
   | 0.4 – 0.74       | ⭐⭐☆  | 2 stars |
   | 0.75 – 1.0       | ⭐⭐⭐ | 3 stars |

3. Stars should animate in (e.g., scale pop) sequentially for a rewarding feel.
4. Use accessible SVG or emoji stars with appropriate `aria-label` (e.g., "2 out of 3 stars").
5. Replace CSS classes `.confidence-bar` / `.confidence-fill` with new star-specific styles.
6. Update all JavaScript that sets `confidenceFill.style.width` / `confidenceFill.style.backgroundColor` to use star logic instead.

## Current Usage

The confidence bar is used in the following locations:

| File                             | Type | Usage                                                                |
| -------------------------------- | ---- | -------------------------------------------------------------------- |
| `templates/learning/repeat.html` | HTML | `.confidence-bar` > `.confidence-fill#confidenceFill`                |
| `static/js/speech.js`            | JS   | `confidenceFill.style.width`, `confidenceFill.style.backgroundColor` |
| `static/css/learning.css`        | CSS  | `.confidence-bar`, `.confidence-fill` style definitions              |

## Solution Options

### Option A: Emoji Stars with CSS Animation

Use Unicode star characters (★ / ☆) styled with CSS. Animate each star with a `@keyframes` scale-pop effect using `animation-delay` for sequential reveal.

**Pros:**

- No additional assets (SVG, images) needed.
- Simple HTML — just `<span>` elements with star characters.
- Easy to implement and maintain.
- Works across all modern browsers.

**Cons:**

- Star appearance varies slightly across OS/browser (emoji rendering).
- Limited styling control compared to SVG.

### Option B: SVG Stars with CSS Animation

Use inline SVG `<polygon>` star shapes with fill color toggled between gold (filled) and grey (empty). Animate with CSS `@keyframes`.

**Pros:**

- Pixel-perfect consistency across browsers.
- Full control over color, size, stroke, and animation.
- Better accessibility (SVGs can carry `role` and `aria-label`).

**Cons:**

- More verbose HTML.
- Slightly more complex to implement.

### Option C: CSS-only Stars (Background Image)

Use a single `<div>` with `background-image` of star sprites and `background-position` to control fill level.

**Pros:**

- Compact HTML.

**Cons:**

- Harder to animate sequentially.
- Requires a sprite image asset.
- Less accessible.

## Recommended Solution

**Option A: Emoji Stars with CSS Animation.**

Simplest approach with no new assets. The stars render well at the large sizes used in a children's app. Each star is a `<span>` with a class toggled between `star-filled` and `star-empty`, with `animation-delay` for the sequential pop effect. An `aria-label` on the container provides accessibility.

### Implementation Sketch

**HTML:**

```html
<div class="star-rating" id="starRating" aria-label="0 out of 3 stars">
  <span class="star star-empty" id="star1">★</span>
  <span class="star star-empty" id="star2">★</span>
  <span class="star star-empty" id="star3">★</span>
</div>
```

**CSS:**

```css
.star-rating {
  font-size: 2.5rem;
  text-align: center;
}
.star {
  display: inline-block;
  color: #ddd;
  transition: color 0.3s;
}
.star-filled {
  color: #ffd700;
  animation: star-pop 0.4s ease;
}
.star-empty {
  color: #ddd;
}
@keyframes star-pop {
  0% {
    transform: scale(0);
  }
  60% {
    transform: scale(1.3);
  }
  100% {
    transform: scale(1);
  }
}
```

**JS:**

```javascript
function showStars(confidence) {
  const stars = confidence >= 0.75 ? 3 : confidence >= 0.4 ? 2 : 1;
  const container = document.getElementById("starRating");
  container.setAttribute("aria-label", stars + " out of 3 stars");
  for (let i = 1; i <= 3; i++) {
    const el = document.getElementById("star" + i);
    if (i <= stars) {
      el.classList.replace("star-empty", "star-filled");
      el.style.animationDelay = (i - 1) * 0.2 + "s";
    }
  }
}
```
