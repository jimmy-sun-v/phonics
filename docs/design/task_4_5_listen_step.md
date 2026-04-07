# Design: Task 4.5 – Learning Loop – Listen Step

## Overview

Build the "Listen" step of the learning loop: TTS audio plays the phoneme sound, symbol is shown prominently, with replay and proceed controls.

## Dependencies

- Task 3.14 (TTS API)
- Task 4.4 (Phoneme list — user arrives from here)

## Detailed Design

### URL Route

| URL | View | Template |
|-----|------|----------|
| `/learn/<symbol>/listen/` | `listen_step_view` | `learning/listen.html` |

### Django View

```python
# apps/phonics/views.py (add)
def listen_step_view(request, symbol):
    phoneme = get_phoneme_detail(symbol)
    if phoneme is None:
        return redirect("phonics:category-list-page")
    return render(request, "learning/listen.html", {"phoneme": phoneme})
```

### Template

**File: `templates/learning/listen.html`**

```html
{% extends "base.html" %}
{% load static %}

{% block title %}Listen: {{ phoneme.symbol }}{% endblock %}
{% block header_title %}Listen!{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/learning.css' %}">
{% endblock %}

{% block content %}
<div class="learning-step listen-step">
    <div class="step-indicator">
        <span class="step active">Listen</span>
        <span class="step">See</span>
        <span class="step">Say</span>
        <span class="step">Play</span>
        <span class="step">Done!</span>
    </div>

    <div class="phoneme-display">
        <span class="phoneme-large" aria-label="Phoneme {{ phoneme.symbol }}">
            {{ phoneme.symbol }}
        </span>
    </div>

    <div class="audio-controls">
        <button
            class="btn-primary btn-round listen-btn"
            id="listenBtn"
            aria-label="Listen to the sound"
            data-phoneme="{{ phoneme.symbol }}"
            data-example="{{ phoneme.example_words.0 }}">
            🔊 Listen
        </button>

        <button
            class="btn-secondary listen-again-btn"
            id="listenAgainBtn"
            style="display:none;"
            aria-label="Listen again">
            🔁 Again
        </button>
    </div>

    <div class="step-nav">
        <a href="{% url 'phonics:learning-observe' phoneme.symbol %}"
           class="btn-primary"
           id="nextBtn"
           style="display:none;">
            Next →
        </a>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/learning.js' %}"></script>
<script>
    initListenStep('{{ phoneme.symbol }}', '{{ phoneme.example_words.0 }}');
</script>
{% endblock %}
```

### JavaScript

**File: `static/js/learning.js`**

```javascript
function initListenStep(phoneme, exampleWord) {
    const listenBtn = document.getElementById('listenBtn');
    const againBtn = document.getElementById('listenAgainBtn');
    const nextBtn = document.getElementById('nextBtn');
    let hasListened = false;

    function playSound() {
        const text = exampleWord || phoneme;
        const audio = new Audio(`/api/speech/tts/?text=${encodeURIComponent(text)}`);
        audio.play().then(() => {
            if (!hasListened) {
                hasListened = true;
                againBtn.style.display = '';
                nextBtn.style.display = '';
            }
        }).catch(err => {
            // Autoplay blocked — show listen button prominently
            console.warn('Autoplay blocked:', err);
        });
    }

    listenBtn.addEventListener('click', playSound);
    againBtn.addEventListener('click', playSound);

    // Attempt autoplay (may be blocked by browser policy)
    playSound();
}
```

### CSS

**File: `static/css/learning.css`**

```css
.learning-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2rem;
    padding: 1rem;
    text-align: center;
}

/* Step indicator */
.step-indicator {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    justify-content: center;
}

.step-indicator .step {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    background: #e0e0e0;
    color: #888;
}

.step-indicator .step.active {
    background: #4a90d9;
    color: white;
}

/* Large phoneme display */
.phoneme-display {
    padding: 2rem;
}

.phoneme-large {
    font-size: 5rem;
    font-weight: 700;
    font-family: "Courier New", monospace;
    color: #333;
}

/* Audio controls */
.audio-controls {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    justify-content: center;
}

.btn-round {
    border-radius: 50%;
    width: 80px;
    height: 80px;
    font-size: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
}

.step-nav {
    margin-top: 1rem;
}
```

## Acceptance Criteria

- [ ] Audio plays on page load (or on first tap for mobile autoplay)
- [ ] Phoneme symbol shown large and centered
- [ ] "Listen Again" button replays audio
- [ ] "Next" button appears after first listen and proceeds to Observe
- [ ] Step indicator shows "Listen" as active

## Test Strategy

- Manual: Select phoneme → audio plays (or tap to play on mobile)
- Manual: "Listen Again" replays; "Next" navigates to Observe
- Manual: Test on mobile browser for autoplay policy handling
