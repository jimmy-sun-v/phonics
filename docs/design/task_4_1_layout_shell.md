# Design: Task 4.1 – Responsive Layout Shell & CSS Framework

## Overview

Implement the main app layout shell with header, main content area, and navigation. Mobile-first CSS with breakpoints for mobile, tablet, and desktop.

## Dependencies

- Task 1.9 (Static files & base template)

## Detailed Design

### Files

| File | Purpose |
|------|---------|
| `static/css/layout.css` | Layout grid, breakpoints, nav styles |
| `templates/base.html` | Updated with layout structure |
| `templates/components/header.html` | Header partial |

### `static/css/layout.css`

```css
/* === App Shell Layout === */
.app-shell {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

/* === Header === */
.app-header {
    background: linear-gradient(135deg, #4a90d9 0%, #357abd 100%);
    color: white;
    padding: 0.75rem 1rem;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-content {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
}

/* === Main Content === */
.main-content {
    flex: 1;
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
}

/* === Bottom Navigation (Mobile) === */
.app-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    border-top: 2px solid #e0e0e0;
    display: flex;
    justify-content: space-around;
    padding: 0.5rem 0;
    z-index: 100;
}

.nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-decoration: none;
    color: #666;
    font-size: 0.75rem;
    min-height: 48px;
    min-width: 48px;
    justify-content: center;
    padding: 0.25rem 0.5rem;
    border-radius: 8px;
    transition: background-color 0.2s;
}

.nav-item:hover, .nav-item:focus {
    background-color: #f0f4ff;
    color: #4a90d9;
}

.nav-item.active {
    color: #4a90d9;
    font-weight: 600;
}

.nav-icon {
    font-size: 1.5rem;
    margin-bottom: 0.125rem;
}

/* Add bottom padding for fixed nav */
body {
    padding-bottom: 70px;
}

/* === Content Grid Helpers === */
.card-grid {
    display: grid;
    gap: 1rem;
    grid-template-columns: 1fr;
}

.card {
    background: white;
    border-radius: 16px;
    padding: 1.25rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    text-align: center;
    cursor: pointer;
    transition: transform 0.15s, box-shadow 0.15s;
    min-height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.card:hover, .card:focus {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card:active {
    transform: translateY(0);
}

/* === Large Action Button === */
.btn-primary {
    background-color: #4a90d9;
    color: white;
    border: none;
    border-radius: 24px;
    padding: 0.875rem 2rem;
    font-size: 1.125rem;
    font-weight: 600;
    min-height: 48px;
    min-width: 48px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.btn-primary:hover, .btn-primary:focus {
    background-color: #357abd;
}

.btn-secondary {
    background-color: transparent;
    color: #4a90d9;
    border: 2px solid #4a90d9;
    border-radius: 24px;
    padding: 0.875rem 2rem;
    font-size: 1.125rem;
    font-weight: 600;
    min-height: 48px;
    min-width: 48px;
    cursor: pointer;
}

/* === Responsive: Tablet (768px+) === */
@media (min-width: 768px) {
    .card-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .main-content {
        padding: 1.5rem;
    }

    body {
        padding-bottom: 0;
    }

    /* Side nav on tablet */
    .app-nav {
        position: static;
        flex-direction: column;
        width: 200px;
        border-top: none;
        border-right: 2px solid #e0e0e0;
        padding: 1rem;
    }

    .app-shell {
        flex-direction: row;
    }

    .app-shell > .main-content {
        flex: 1;
    }
}

/* === Responsive: Desktop (1024px+) === */
@media (min-width: 1024px) {
    .card-grid {
        grid-template-columns: repeat(3, 1fr);
    }

    .main-content {
        padding: 2rem;
    }
}
```

### Updated `templates/base.html`

```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{% block title %}Phonics Tutor{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'css/base.css' %}">
    <link rel="stylesheet" href="{% static 'css/layout.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body>
<div class="app-shell">
    {% include "components/header.html" %}

    <main class="main-content" role="main">
        {% block content %}{% endblock %}
    </main>

    <nav class="app-nav" role="navigation" aria-label="Main navigation">
        {% block nav %}
        <a href="/" class="nav-item" aria-label="Home">
            <span class="nav-icon">🏠</span>
            <span>Home</span>
        </a>
        <a href="/phonics/" class="nav-item" aria-label="Learn">
            <span class="nav-icon">📚</span>
            <span>Learn</span>
        </a>
        <a href="/games/" class="nav-item" aria-label="Games">
            <span class="nav-icon">🎮</span>
            <span>Games</span>
        </a>
        {% endblock %}
    </nav>
</div>

{% block extra_js %}{% endblock %}
</body>
</html>
```

### `templates/components/header.html`

```html
<header class="app-header">
    <div class="header-content">
        {% block mascot %}{% endblock %}
        <h1 class="app-title">{% block header_title %}Phonics Tutor{% endblock %}</h1>
    </div>
</header>
```

### Design Decisions

| Decision | Rationale |
|----------|-----------|
| Mobile-first CSS | Target audience (children) primarily uses tablets/phones |
| Fixed bottom nav on mobile | Thumb-reachable navigation for children |
| 48px min touch targets | WCAG 2.5.5 Target Size compliance |
| Sticky header | Consistent mascot/branding visibility |
| Card-based layout | Large, clear interactive areas for children |
| No CSS framework (Bootstrap/Tailwind) | Minimal JS per App_Overview §9.1; custom styles more appropriate for child UI |

## Acceptance Criteria

- [ ] Layout adapts at 3 breakpoints (mobile / tablet / desktop)
- [ ] No horizontal scroll at any width
- [ ] All tap targets ≥ 48×48px
- [ ] WCAG-aware color contrast ≥ 4.5:1
- [ ] Bottom nav on mobile, side nav on tablet+
- [ ] Header is sticky

## Test Strategy

- Manual: Chrome DevTools → iPhone SE (375px), iPad (768px), Desktop (1280px)
- Manual: Contrast checker on all color combinations
- Manual: Verify no horizontal overflow at 320px minimum width
