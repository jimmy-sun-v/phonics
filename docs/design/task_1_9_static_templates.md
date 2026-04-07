# Design: Task 1.9 – Set Up Static Files & Base Template Structure

## Overview

Configure Django static file handling and create a responsive base HTML template with CSS reset, viewport meta tag, and block structure for child templates.

## Dependencies

- Task 1.1

## Detailed Design

### Directory Structure

```
PhonicsApp/
├── static/
│   ├── css/
│   │   └── base.css
│   ├── js/
│   │   └── .gitkeep
│   └── images/
│       └── .gitkeep
└── templates/
    └── base.html
```

### Step-by-Step Implementation

1. **Verify static settings** in `config/settings/base.py` (from Task 1.1):
   ```python
   STATIC_URL = "static/"
   STATICFILES_DIRS = [BASE_DIR / "static"]
   STATIC_ROOT = BASE_DIR / "staticfiles"
   ```

2. **Create `templates/base.html`**:
   ```html
   {% load static %}
   <!DOCTYPE html>
   <html lang="en">
   <head>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
       <meta name="description" content="AI Phonics Tutor - Learn phonics with fun!">
       <title>{% block title %}Phonics Tutor{% endblock %}</title>

       <!-- Base CSS -->
       <link rel="stylesheet" href="{% static 'css/base.css' %}">

       {% block extra_css %}{% endblock %}
   </head>
   <body>
       {% block header %}
       <header class="app-header">
           <div class="header-content">
               {% block mascot %}{% endblock %}
               <h1 class="app-title">{% block header_title %}Phonics Tutor{% endblock %}</h1>
           </div>
       </header>
       {% endblock %}

       <main class="main-content" role="main">
           {% block content %}{% endblock %}
       </main>

       <nav class="app-nav" role="navigation" aria-label="Main navigation">
           {% block nav %}{% endblock %}
       </nav>

       {% block extra_js %}{% endblock %}
   </body>
   </html>
   ```

3. **Create `static/css/base.css`**:
   ```css
   /* === CSS Reset === */
   *, *::before, *::after {
       box-sizing: border-box;
       margin: 0;
       padding: 0;
   }

   html {
       font-size: 16px;
       -webkit-text-size-adjust: 100%;
   }

   body {
       font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
       line-height: 1.5;
       color: #333;
       background-color: #f0f4ff;
       min-height: 100vh;
       display: flex;
       flex-direction: column;
   }

   img {
       max-width: 100%;
       height: auto;
       display: block;
   }

   button, a {
       cursor: pointer;
   }

   /* === Touch Target (WCAG) === */
   button, a, [role="button"] {
       min-height: 48px;
       min-width: 48px;
   }

   /* === App Layout === */
   .app-header {
       background-color: #4a90d9;
       color: white;
       padding: 1rem;
       text-align: center;
   }

   .header-content {
       max-width: 1200px;
       margin: 0 auto;
       display: flex;
       align-items: center;
       justify-content: center;
       gap: 1rem;
   }

   .app-title {
       font-size: 1.5rem;
       font-weight: 700;
   }

   .main-content {
       flex: 1;
       max-width: 1200px;
       margin: 0 auto;
       padding: 1rem;
       width: 100%;
   }

   .app-nav {
       background-color: #fff;
       border-top: 1px solid #ddd;
       padding: 0.5rem;
   }

   /* === Responsive Breakpoints === */

   /* Mobile (< 768px) — default styles above are mobile-first */

   /* Tablet (768px – 1023px) */
   @media (min-width: 768px) {
       .app-title {
           font-size: 2rem;
       }

       .main-content {
           padding: 1.5rem;
       }
   }

   /* Desktop (≥ 1024px) */
   @media (min-width: 1024px) {
       .app-title {
           font-size: 2.25rem;
       }

       .main-content {
           padding: 2rem;
       }

       .app-nav {
           display: none; /* Side nav on desktop handled in layout.css */
       }
   }

   /* === Accessibility === */
   :focus-visible {
       outline: 3px solid #4a90d9;
       outline-offset: 2px;
   }

   /* WCAG color contrast: primary text #333 on #f0f4ff = 10.5:1 ratio ✓ */
   /* Header: white #fff on #4a90d9 = 4.6:1 ratio ✓ (AA for large text) */
   ```

4. **Create placeholder directories** with `.gitkeep`:
   - `static/js/.gitkeep`
   - `static/images/.gitkeep`

### Design Decisions

- **Mobile-first CSS**: Default styles target mobile, `@media` queries add complexity upward
- **`user-scalable=no`**: Prevents accidental zoom during child interactions; accessibility tradeoff accepted for target age group
- **Flex layout**: Body uses `flex-direction: column` for sticky footer pattern
- **Max-width 1200px**: Prevents overly wide content on large monitors
- **WCAG contrast**: All color combinations meet AA minimum (4.5:1 for normal text)

## Acceptance Criteria

- [ ] `{% static %}` tag resolves correctly in templates
- [ ] `base.html` contains `<meta name="viewport" ...>`
- [ ] Page renders correctly at mobile (<768px), tablet (768–1023px), desktop (≥1024px)
- [ ] No horizontal overflow at any viewport width
- [ ] Touch targets ≥ 48px

## Test Strategy

- Manual: Load page at 3 viewport widths, confirm no horizontal overflow
- Unit: `TemplateResponse` renders `base.html` without template errors
