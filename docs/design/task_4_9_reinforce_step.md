# Design: Task 4.9 – Learning Loop – Reinforce Step

## Overview

Build the "Reinforce" step with celebration animation, encouraging message, progress indicator, and navigation to continue learning.

## Dependencies

- Task 4.8 (Practice step)
- Task 3.3 (Progress tracking)

## Detailed Design

### URL Route

| URL | View | Template |
|-----|------|----------|
| `/phonics/learn/<symbol>/reinforce/` | `reinforce_step_view` | `learning/reinforce.html` |

### Template

**File: `templates/learning/reinforce.html`**

```html
{% extends "base.html" %}
{% load static %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/learning.css' %}">
<link rel="stylesheet" href="{% static 'css/animations.css' %}">
{% endblock %}

{% block content %}
<div class="learning-step reinforce-step">
    <div class="step-indicator">
        <span class="step done">Listen</span>
        <span class="step done">See</span>
        <span class="step done">Say</span>
        <span class="step done">Play</span>
        <span class="step active">Done!</span>
    </div>

    <div class="celebration">
        <div class="stars-container" id="starsContainer"></div>
        <span class="celebration-emoji">⭐</span>
        <h2 class="celebration-text">Amazing work!</h2>
        <p class="celebration-sub">You practiced "{{ phoneme.symbol }}"!</p>
    </div>

    <div class="progress-section">
        <div class="progress-bar">
            <div class="progress-fill" style="width: {{ completion_pct }}%"></div>
        </div>
        <p class="progress-text">{{ completed_count }} of {{ total_count }} sounds learned</p>
    </div>

    <div class="step-nav">
        {% if next_phoneme %}
        <a href="{% url 'phonics:learning-listen' next_phoneme.symbol %}" class="btn-primary">
            Next Sound →
        </a>
        {% else %}
        <a href="{% url 'phonics:category-list-page' %}" class="btn-primary">
            Back to Menu
        </a>
        {% endif %}
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/rewards.js' %}"></script>
{% endblock %}
```

### Reward Animation JS

**File: `static/js/rewards.js`**

```javascript
document.addEventListener('DOMContentLoaded', () => {
    // Set mascot to happy
    if (typeof setMascotState === 'function') {
        setMascotState('happy');
    }

    // Create star burst animation
    const container = document.getElementById('starsContainer');
    if (container) {
        for (let i = 0; i < 12; i++) {
            const star = document.createElement('span');
            star.textContent = ['⭐', '🌟', '✨'][i % 3];
            star.className = 'floating-star';
            star.style.left = Math.random() * 100 + '%';
            star.style.animationDelay = (Math.random() * 0.5) + 's';
            star.style.animationDuration = (1 + Math.random()) + 's';
            container.appendChild(star);
        }
    }
});
```

### CSS additions to `static/css/animations.css`

```css
.celebration {
    text-align: center;
    position: relative;
    padding: 2rem 0;
}

.celebration-emoji {
    font-size: 4rem;
    animation: scale-in 0.6s ease-out;
}

.celebration-text {
    font-size: 1.75rem;
    color: #4a90d9;
    margin-top: 1rem;
}

.stars-container {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
    overflow: hidden;
}

.floating-star {
    position: absolute;
    font-size: 1.5rem;
    animation: float-up 1.5s ease-out forwards;
    opacity: 0;
}

@keyframes float-up {
    0% { transform: translateY(100px); opacity: 0; }
    30% { opacity: 1; }
    100% { transform: translateY(-100px); opacity: 0; }
}

.progress-bar {
    width: 100%;
    max-width: 400px;
    height: 16px;
    background: #e0e0e0;
    border-radius: 8px;
    overflow: hidden;
    margin: 0 auto;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #4CAF50, #8BC34A);
    border-radius: 8px;
    transition: width 1s ease-out;
}

.progress-text {
    text-align: center;
    color: #666;
    margin-top: 0.5rem;
}
```

## Acceptance Criteria

- [ ] Encouraging message displayed (never "wrong")
- [ ] Star animation plays on load
- [ ] Mascot switches to happy state
- [ ] Progress bar shows completion percentage
- [ ] "Next Sound" or "Back to Menu" navigation works

## Test Strategy

- Manual: Complete phoneme → reinforce shows celebration
- Manual: Progress bar advances correctly
- Manual: Visual works at all breakpoints
