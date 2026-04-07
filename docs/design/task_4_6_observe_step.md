# Design: Task 4.6 – Learning Loop – Observe Step

## Overview

Build the "Observe" step: display the phoneme letter(s) with animation and show an example word with the phoneme highlighted.

## Dependencies

- Task 4.5 (Listen step — user arrives from here)

## Detailed Design

### URL Route

| URL | View | Template |
|-----|------|----------|
| `/phonics/learn/<symbol>/observe/` | `observe_step_view` | `learning/observe.html` |

### Template

**File: `templates/learning/observe.html`**

```html
{% extends "base.html" %}
{% load static %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/learning.css' %}">
<link rel="stylesheet" href="{% static 'css/animations.css' %}">
{% endblock %}

{% block content %}
<div class="learning-step observe-step">
    <div class="step-indicator">
        <span class="step done">Listen</span>
        <span class="step active">See</span>
        <span class="step">Say</span>
        <span class="step">Play</span>
        <span class="step">Done!</span>
    </div>

    <div class="observe-display">
        <span class="letter-animate" aria-label="Letter {{ phoneme.symbol }}">
            {{ phoneme.symbol }}
        </span>
    </div>

    <div class="example-word" aria-label="Example word">
        {% for part in word_parts %}
            {% if part.highlight %}
                <span class="highlight">{{ part.text }}</span>
            {% else %}
                <span>{{ part.text }}</span>
            {% endif %}
        {% endfor %}
    </div>

    <div class="step-nav">
        <a href="{% url 'phonics:learning-repeat' phoneme.symbol %}" class="btn-primary">
            Next →
        </a>
    </div>
</div>
{% endblock %}
```

### Django View

```python
# apps/phonics/page_views.py (add)
def observe_step_view(request, symbol):
    phoneme = get_phoneme_detail(symbol)
    if phoneme is None:
        return redirect("phonics:category-list-page")

    # Split example word to highlight the phoneme
    example = phoneme.example_words[0] if phoneme.example_words else ""
    word_parts = _split_word_for_highlight(example, symbol)

    return render(request, "learning/observe.html", {
        "phoneme": phoneme,
        "word_parts": word_parts,
    })


def _split_word_for_highlight(word: str, phoneme_symbol: str) -> list[dict]:
    """Split a word into parts with the phoneme highlighted.

    Example: _split_word_for_highlight("ship", "sh")
    → [{"text": "sh", "highlight": True}, {"text": "ip", "highlight": False}]
    """
    symbol = phoneme_symbol.replace("_", "")  # Handle magic-e patterns
    lower_word = word.lower()
    idx = lower_word.find(symbol.lower())

    if idx == -1:
        return [{"text": word, "highlight": False}]

    parts = []
    if idx > 0:
        parts.append({"text": word[:idx], "highlight": False})
    parts.append({"text": word[idx:idx + len(symbol)], "highlight": True})
    if idx + len(symbol) < len(word):
        parts.append({"text": word[idx + len(symbol):], "highlight": False})
    return parts
```

### Animations CSS

**File: `static/css/animations.css`**

```css
/* === Scale-in Animation === */
.letter-animate {
    font-size: 6rem;
    font-weight: 700;
    font-family: "Courier New", monospace;
    color: #4a90d9;
    display: inline-block;
    animation: scale-in 0.6s ease-out;
}

@keyframes scale-in {
    0% {
        transform: scale(0.3);
        opacity: 0;
    }
    60% {
        transform: scale(1.1);
        opacity: 1;
    }
    100% {
        transform: scale(1);
    }
}

/* === Phoneme Highlight in Word === */
.example-word {
    font-size: 2.5rem;
    margin-top: 1.5rem;
}

.example-word .highlight {
    color: #4a90d9;
    font-weight: 700;
    text-decoration: underline;
    text-decoration-color: #ff9800;
    text-underline-offset: 4px;
}
```

## Acceptance Criteria

- [ ] Letter(s) animate in on page load (scale-in effect)
- [ ] Example word shows phoneme highlighted (e.g., **sh**ip)
- [ ] Animation is subtle, not distracting (< 1 second)
- [ ] "Next" proceeds to Repeat step
- [ ] Step indicator shows "See" as active

## Test Strategy

- Manual: Verify animation plays on page load
- Manual: Phoneme highlighted in example word correctly
- Manual: Works at all breakpoints
