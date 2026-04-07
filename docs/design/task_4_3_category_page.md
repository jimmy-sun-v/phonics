# Design: Task 4.3 – Phonics Category Selection Page

## Overview

Build a page displaying all 6 phonics categories as large, tappable cards. Fetches data from the categories API.

## Dependencies

- Task 3.11 (Phonics API)
- Task 4.1 (Layout shell)

## Detailed Design

### URL Route

| URL | View | Template |
|-----|------|----------|
| `/phonics/` | `category_list_view` | `phonics/categories.html` |

### Django View (Template View)

**File: `apps/phonics/page_views.py`** (template views in separate file from API views)

```python
from django.shortcuts import render
from apps.phonics.services import get_all_categories


def category_list_view(request):
    """Render the phonics category selection page."""
    categories = get_all_categories()

    # Category display metadata (icons/emoji + colors)
    category_meta = {
        "single_letter": {"icon": "🔤", "color": "#4CAF50"},
        "digraph": {"icon": "🔗", "color": "#2196F3"},
        "blend": {"icon": "🎨", "color": "#FF9800"},
        "long_vowel": {"icon": "📏", "color": "#9C27B0"},
        "r_controlled": {"icon": "🎯", "color": "#F44336"},
        "diphthong": {"icon": "🎵", "color": "#00BCD4"},
    }

    for cat in categories:
        meta = category_meta.get(cat["value"], {})
        cat["icon"] = meta.get("icon", "📖")
        cat["color"] = meta.get("color", "#666")

    return render(request, "phonics/categories.html", {"categories": categories})
```

### Template

**File: `templates/phonics/categories.html`**

```html
{% extends "base.html" %}
{% load static %}

{% block title %}Choose a Sound Group{% endblock %}
{% block header_title %}Pick a Sound!{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/phonics.css' %}">
{% endblock %}

{% block content %}
<div class="category-page">
    <p class="page-instruction" aria-live="polite">Tap to start!</p>

    <div class="card-grid category-grid">
        {% for cat in categories %}
        <a href="{% url 'phonics:phoneme-list-page' cat.value %}"
           class="card category-card"
           style="border-left: 4px solid {{ cat.color }}"
           aria-label="{{ cat.label }} - {{ cat.count }} sounds">
            <span class="category-icon" aria-hidden="true">{{ cat.icon }}</span>
            <span class="category-label">{{ cat.label }}</span>
            <span class="category-count">{{ cat.count }} sounds</span>
        </a>
        {% endfor %}
    </div>
</div>
{% endblock %}
```

### CSS

**File: `static/css/phonics.css`**

```css
.page-instruction {
    text-align: center;
    font-size: 1.25rem;
    color: #666;
    margin-bottom: 1.5rem;
}

.category-card {
    flex-direction: column;
    gap: 0.5rem;
    padding: 1.5rem;
    min-height: 120px;
}

.category-icon {
    font-size: 2.5rem;
}

.category-label {
    font-size: 1.125rem;
    font-weight: 600;
    color: #333;
}

.category-count {
    font-size: 0.875rem;
    color: #888;
}

/* Audio cue click handler — plays a subtle tap sound */
.category-card:active {
    transform: scale(0.97);
}

/* === Responsive === */
/* Mobile: 1-column */
.category-grid {
    grid-template-columns: 1fr;
}

/* Tablet: 2-column */
@media (min-width: 768px) {
    .category-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .category-card {
        min-height: 140px;
    }
}

/* Desktop: 3-column */
@media (min-width: 1024px) {
    .category-grid {
        grid-template-columns: repeat(3, 1fr);
    }
}
```

### URL Configuration

In `apps/phonics/page_urls.py`, add the template view:
```python
path("", page_views.category_list_view, name="category-list-page"),
```

In `config/urls.py`, add:
```python
path("phonics/", include("apps.phonics.page_urls")),  # Template views
path("api/phonics/", include("apps.phonics.urls")),  # API views
```

Note: Page views use `apps/phonics/page_urls.py` (with `app_name = "phonics"`) while API views use `apps/phonics/urls.py` (no `app_name`) to avoid namespace conflicts.

### Audio Cue (Optional)

```javascript
// static/js/phonics.js
document.querySelectorAll('.category-card').forEach(card => {
    card.addEventListener('click', () => {
        const audio = new Audio('/static/audio/tap.mp3');
        audio.volume = 0.3;
        audio.play().catch(() => {}); // Ignore autoplay errors
    });
});
```

## Acceptance Criteria

- [ ] All 6 categories displayed as cards
- [ ] Cards are large, tappable (≥ 48px touch target)
- [ ] No text > 5 words on any card
- [ ] Mobile: 1 column; Tablet: 2 columns; Desktop: 3 columns
- [ ] Each card links to the phoneme list for that category

## Test Strategy

- Manual: All categories visible and tappable on mobile/tablet/desktop
- Unit: View returns correct template context with 6 categories
- Manual: Verify card links navigate correctly
