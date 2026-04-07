# Design: Task 4.10 – Game – Sound → Picture Matching

## Overview

Build the Sound-Picture matching game: audio plays a phoneme sound, child selects the correct picture from 3-4 options.

## Dependencies

- Task 3.14 (TTS API)
- Task 3.15 (Games API)
- Task 4.1 (Layout)

## Detailed Design

### URL Route

| URL | View | Template |
|-----|------|----------|
| `/games/sound_picture/<symbol>/` | `sound_picture_view` | `games/sound_picture.html` |

### Game Mechanics

1. Audio plays the target sound/word automatically
2. 4 picture cards displayed (1 correct + 3 distractors)
3. Child taps a picture
4. Correct → celebration animation + mascot happy + point
5. Incorrect → gentle wobble + encouragement (never "wrong")
6. After correct answer, can proceed or play again

### Template

**File: `templates/games/sound_picture.html`**

```html
{% extends "base.html" %}
{% load static %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/games.css' %}">
{% endblock %}

{% block content %}
<div class="game-container sound-picture-game">
    <div class="game-header">
        <button class="btn-secondary" id="playSound" aria-label="Play sound again">
            🔊 Hear Sound
        </button>
        <span class="game-score" id="score">⭐ 0</span>
    </div>

    <p class="game-instruction">Tap the right picture!</p>

    <div class="picture-grid" id="pictureGrid">
        {% for option in options %}
        <button class="picture-card"
                data-word="{{ option.word }}"
                data-correct="{{ option.is_correct|yesno:'true,false' }}"
                aria-label="{{ option.word }}">
            <img src="{% static option.image_path %}" alt="{{ option.word }}" class="picture-img">
            <span class="picture-label">{{ option.word }}</span>
        </button>
        {% endfor %}
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/games/sound_picture.js' %}"></script>
{% endblock %}
```

### JavaScript

**File: `static/js/games/sound_picture.js`**

```javascript
document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.picture-card');
    const playBtn = document.getElementById('playSound');
    const scoreEl = document.getElementById('score');
    let currentScore = 0;

    playBtn.addEventListener('click', playTargetSound);
    playTargetSound(); // Auto-play on load

    cards.forEach(card => {
        card.addEventListener('click', () => handleSelection(card));
    });

    function playTargetSound() {
        const correctCard = document.querySelector('[data-correct="true"]');
        const word = correctCard.dataset.word;
        const audio = new Audio(`/api/speech/tts/?text=${encodeURIComponent(word)}`);
        audio.play().catch(() => {});
    }

    function handleSelection(card) {
        if (card.dataset.correct === 'true') {
            card.classList.add('correct');
            currentScore++;
            scoreEl.textContent = `⭐ ${currentScore}`;
            if (typeof flashMascotState === 'function') flashMascotState('happy');
        } else {
            card.classList.add('incorrect');
            card.classList.add('wobble');
            setTimeout(() => card.classList.remove('wobble'), 500);
        }
    }
});
```

### CSS

**File: `static/css/games.css`**

```css
.game-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 1rem;
}

.game-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.game-score {
    font-size: 1.5rem;
    font-weight: 600;
}

.game-instruction {
    text-align: center;
    font-size: 1.25rem;
    margin-bottom: 1.5rem;
}

.picture-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
}

.picture-card {
    background: white;
    border: 3px solid #e0e0e0;
    border-radius: 16px;
    padding: 1rem;
    cursor: pointer;
    transition: all 0.2s;
    min-height: 120px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
}

.picture-card.correct {
    border-color: #4CAF50;
    background: #f1f8e9;
}

.picture-card.incorrect {
    opacity: 0.5;
}

.picture-img {
    max-width: 80px;
    max-height: 80px;
}

@keyframes wobble {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}

.wobble { animation: wobble 0.3s ease-in-out; }

/* Tablet/Desktop: 1x4 row */
@media (min-width: 768px) {
    .picture-grid {
        grid-template-columns: repeat(4, 1fr);
    }
}
```

## Acceptance Criteria

- [ ] Audio plays phoneme sound
- [ ] 3-4 picture options displayed as tappable cards
- [ ] Correct → celebration, incorrect → wobble (never "wrong")
- [ ] Mobile: 2×2 grid; Tablet+: 1×4 row
- [ ] Touch and mouse input both work

## Test Strategy

- Manual: Play game, select correct picture → celebration
- Manual: Select incorrect → wobble + try again
- Manual: Touch-friendly on mobile
