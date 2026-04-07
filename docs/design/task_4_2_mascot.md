# Design: Task 4.2 – Mascot Component

## Overview

Create a reusable mascot UI component with multiple visual states (idle, happy, encouraging) using CSS classes. Responsive positioning.

## Dependencies

- Task 4.1 (Layout shell)

## Detailed Design

### Files

| File | Purpose |
|------|---------|
| `templates/components/mascot.html` | Mascot template fragment |
| `static/css/mascot.css` | Mascot styles and state animations |
| `static/images/mascot/` | Mascot image assets (SVG preferred) |

### `templates/components/mascot.html`

```html
{# Usage: {% include "components/mascot.html" with state="idle" %} #}
{# States: idle, happy, encouraging #}
{% load static %}
<div class="mascot mascot--{{ state|default:'idle' }}" role="img" aria-label="Friendly owl mascot">
    <img
        src="{% static 'images/mascot/mascot.svg' %}"
        alt="Phonics Tutor Mascot"
        class="mascot__image"
        width="80"
        height="80"
    >
</div>
```

### `static/css/mascot.css`

```css
/* === Mascot Base === */
.mascot {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.3s ease;
}

.mascot__image {
    width: 60px;
    height: 60px;
    object-fit: contain;
}

/* === Mascot States === */
.mascot--idle {
    animation: mascot-breathe 3s ease-in-out infinite;
}

.mascot--happy {
    animation: mascot-bounce 0.6s ease-in-out;
}

.mascot--encouraging {
    animation: mascot-nod 0.8s ease-in-out;
}

/* === Animations === */
@keyframes mascot-breathe {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

@keyframes mascot-bounce {
    0%, 100% { transform: translateY(0); }
    25% { transform: translateY(-10px); }
    50% { transform: translateY(0); }
    75% { transform: translateY(-5px); }
}

@keyframes mascot-nod {
    0%, 100% { transform: rotate(0deg); }
    25% { transform: rotate(5deg); }
    75% { transform: rotate(-5deg); }
}

/* === Responsive: Mobile — Fixed bottom-right === */
@media (max-width: 767px) {
    .app-header .mascot {
        display: none; /* Hide in header on mobile */
    }

    .mascot-mobile {
        position: fixed;
        bottom: 80px; /* Above the nav bar */
        right: 16px;
        z-index: 50;
    }

    .mascot-mobile .mascot__image {
        width: 50px;
        height: 50px;
    }
}

/* === Responsive: Tablet/Desktop — In header === */
@media (min-width: 768px) {
    .mascot-mobile {
        display: none;
    }

    .mascot__image {
        width: 70px;
        height: 70px;
    }
}

@media (min-width: 1024px) {
    .mascot__image {
        width: 80px;
        height: 80px;
    }
}
```

### JavaScript State Control

**File: `static/js/mascot.js`**

```javascript
/**
 * Update the mascot's visual state.
 * @param {'idle'|'happy'|'encouraging'} state
 */
function setMascotState(state) {
    const mascots = document.querySelectorAll('.mascot');
    const validStates = ['idle', 'happy', 'encouraging'];

    if (!validStates.includes(state)) return;

    mascots.forEach(el => {
        // Remove all state classes
        validStates.forEach(s => el.classList.remove(`mascot--${s}`));
        // Add new state
        el.classList.add(`mascot--${state}`);
    });
}

/**
 * Briefly show a state, then return to idle.
 * @param {'happy'|'encouraging'} state
 * @param {number} durationMs
 */
function flashMascotState(state, durationMs = 2000) {
    setMascotState(state);
    setTimeout(() => setMascotState('idle'), durationMs);
}
```

### Placeholder SVG Mascot

Create a simple owl SVG placeholder at `static/images/mascot/mascot.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
  <circle cx="50" cy="50" r="45" fill="#4a90d9" />
  <circle cx="35" cy="40" r="12" fill="white" />
  <circle cx="65" cy="40" r="12" fill="white" />
  <circle cx="35" cy="40" r="6" fill="#333" />
  <circle cx="65" cy="40" r="6" fill="#333" />
  <polygon points="50,50 45,60 55,60" fill="#ff9800" />
  <path d="M30,70 Q50,85 70,70" stroke="#333" stroke-width="3" fill="none" />
</svg>
```

### Integration with base.html

In `templates/base.html`, the header includes the mascot:
```html
{% include "components/header.html" %}
```

In `templates/components/header.html`:
```html
<header class="app-header">
    <div class="header-content">
        {% include "components/mascot.html" with state="idle" %}
        <h1 class="app-title">{% block header_title %}Phonics Tutor{% endblock %}</h1>
    </div>
</header>
```

And a mobile floating mascot in `base.html`:
```html
<div class="mascot-mobile">
    {% include "components/mascot.html" with state="idle" %}
</div>
```

## Acceptance Criteria

- [ ] Mascot visible on all pages
- [ ] 3 CSS states: `.mascot--idle`, `.mascot--happy`, `.mascot--encouraging`
- [ ] In header on tablet/desktop; floating bottom-right on mobile
- [ ] Does not obstruct content or navigation
- [ ] `setMascotState()` JS function changes state

## Test Strategy

- Manual: Verify mascot visible at mobile, tablet, desktop breakpoints
- Manual: Toggle CSS classes in DevTools → confirm animations
- Manual: Verify mascot doesn't block tappable content on mobile
