# Design: Task 4.8 – Learning Loop – Practice Step (Game Launcher)

## Overview

Build the "Practice" step showing available games for the current phoneme. User selects a game or skips to reinforce.

## Dependencies

- Task 3.15 (Games API)
- Task 4.7 (Repeat step)

## Detailed Design

### URL Route

| URL | View | Template |
|-----|------|----------|
| `/phonics/learn/<symbol>/practice/` | `practice_step_view` | `learning/practice.html` |

### Django View

```python
def practice_step_view(request, symbol):
    phoneme = get_phoneme_detail(symbol)
    if phoneme is None:
        return redirect("phonics:category-list-page")

    games = Game.objects.filter(is_active=True, phonemes=phoneme)
    return render(request, "learning/practice.html", {
        "phoneme": phoneme,
        "games": games,
    })
```

### Template

**File: `templates/learning/practice.html`**

```html
{% extends "base.html" %}
{% load static %}

{% block content %}
<div class="learning-step practice-step">
    <div class="step-indicator">
        <span class="step done">Listen</span>
        <span class="step done">See</span>
        <span class="step done">Say</span>
        <span class="step active">Play</span>
        <span class="step">Done!</span>
    </div>

    <p class="instruction">Pick a game!</p>

    {% if games %}
    <div class="card-grid game-grid">
        {% for game in games %}
        <a href="/games/{{ game.game_type }}/{{ phoneme.symbol }}/" class="card game-card">
            <span class="game-icon">
                {% if game.game_type == 'sound_picture' %}🖼️
                {% elif game.game_type == 'beginning_sound' %}🔤
                {% elif game.game_type == 'blend_builder' %}🧩
                {% elif game.game_type == 'balloon_pop' %}🎈
                {% endif %}
            </span>
            <span class="game-name">{{ game.name }}</span>
        </a>
        {% endfor %}
    </div>
    {% else %}
    <p>No games for this sound yet.</p>
    {% endif %}

    <div class="step-nav">
        <a href="{% url 'phonics:learning-reinforce' phoneme.symbol %}" class="btn-secondary">
            Skip →
        </a>
    </div>
</div>
{% endblock %}
```

## Acceptance Criteria

- [ ] Available games for phoneme displayed as cards
- [ ] Each game links to its specific game page
- [ ] "Skip" option proceeds to reinforce step
- [ ] Phoneme with no games → shows message, skip still works

## Test Strategy

- Manual: Games displayed for phonemes with mapped games
- Manual: Phoneme with no games → skip works
- Manual: Responsive at all breakpoints
