# Design: Task 4.4 – Phoneme List Page (Per Category)

## Overview

Build a page listing phonemes within a selected category as tappable tiles, each showing the phoneme symbol and one example word.

## Dependencies

- Task 3.11 (Phonics API)
- Task 4.3 (Category selection page)

## Detailed Design

### URL Route

| URL | View | Template |
|-----|------|----------|
| `/phonics/<category>/` | `phoneme_list_view` | `phonics/phoneme_list.html` |

### Django View

**File: `apps/phonics/views.py`** (add)

```python
from django.shortcuts import render, redirect
from apps.phonics.services import get_phonemes_by_category
from apps.phonics.models import PhonemeCategory


def phoneme_list_view(request, category):
    """Render the phoneme list for a given category."""
    # Validate category
    valid = [c[0] for c in PhonemeCategory.choices]
    if category not in valid:
        return redirect("phonics:category-list-page")

    phonemes = get_phonemes_by_category(category)
    category_label = dict(PhonemeCategory.choices).get(category, category)

    return render(request, "phonics/phoneme_list.html", {
        "phonemes": phonemes,
        "category": category,
        "category_label": category_label,
    })
```

### Template

**File: `templates/phonics/phoneme_list.html`**

```html
{% extends "base.html" %}
{% load static %}

{% block title %}{{ category_label }}{% endblock %}
{% block header_title %}{{ category_label }}{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/phonics.css' %}">
{% endblock %}

{% block content %}
<div class="phoneme-list-page">
    <a href="{% url 'phonics:category-list-page' %}" class="back-link" aria-label="Back to categories">
        ← Back
    </a>

    <div class="card-grid phoneme-grid">
        {% for phoneme in phonemes %}
        <a href="{% url 'phonics:learning-listen' phoneme.symbol %}"
           class="card phoneme-tile"
           aria-label="{{ phoneme.symbol }} as in {{ phoneme.example_words.0 }}">
            <span class="phoneme-symbol">{{ phoneme.symbol }}</span>
            <span class="phoneme-example">{{ phoneme.example_words.0 }}</span>
        </a>
        {% endfor %}
    </div>
</div>
{% endblock %}
```

### CSS (add to `static/css/phonics.css`)

```css
.back-link {
    display: inline-flex;
    align-items: center;
    color: #4a90d9;
    text-decoration: none;
    font-size: 1rem;
    min-height: 48px;
    margin-bottom: 1rem;
}

.phoneme-tile {
    flex-direction: column;
    gap: 0.25rem;
    padding: 1.25rem;
    min-height: 100px;
}

.phoneme-symbol {
    font-size: 2rem;
    font-weight: 700;
    color: #333;
    font-family: "Courier New", monospace;
}

.phoneme-example {
    font-size: 0.875rem;
    color: #888;
    font-style: italic;
}

/* === Responsive Phoneme Grid === */
.phoneme-grid {
    grid-template-columns: repeat(2, 1fr);
}

@media (min-width: 768px) {
    .phoneme-grid {
        grid-template-columns: repeat(3, 1fr);
    }
}

@media (min-width: 1024px) {
    .phoneme-grid {
        grid-template-columns: repeat(4, 1fr);
    }
}
```

### URL Configuration

In `apps/phonics/urls.py`:
```python
path("<str:category>/", views.phoneme_list_view, name="phoneme-list-page"),
```

## Acceptance Criteria

- [ ] Phonemes displayed in `display_order`
- [ ] Each tile shows symbol + one example word (≤ 5 words)
- [ ] Back navigation to categories
- [ ] Touch target ≥ 48px
- [ ] Mobile: 2-column; Tablet: 3-column; Desktop: 4-column

## Test Strategy

- Manual: Navigate from category → phoneme list, verify items
- Manual: Test at mobile, tablet, desktop breakpoints
- Unit: View returns correct phonemes for category
