# Design: Task 5.3 – Diagnostics Dashboard UI

## Overview

Build an HTML dashboard page for parents/teachers to view diagnostics: summary stats, per-phoneme accuracy chart, and daily activity chart. Uses Chart.js for visualization.

## Dependencies

- Task 5.2 (Diagnostics API)
- Task 4.1 (Layout)

## Detailed Design

### URL Route

| URL | View | Template |
|-----|------|----------|
| `/diagnostics/` | `diagnostics_dashboard_view` | `diagnostics/dashboard.html` |

### Template

**File: `templates/diagnostics/dashboard.html`**

```html
{% extends "base.html" %}
{% load static %}

{% block title %}Diagnostics Dashboard{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/dashboard.css' %}">
{% endblock %}

{% block content %}
<div class="dashboard">
    <h2>How we're doing</h2>

    <div class="stats-row" id="statsRow">
        <div class="stat-card">
            <span class="stat-value" id="totalAttempts">—</span>
            <span class="stat-label">Total Tries</span>
        </div>
        <div class="stat-card">
            <span class="stat-value" id="avgConfidence">—</span>
            <span class="stat-label">Avg Confidence</span>
        </div>
        <div class="stat-card">
            <span class="stat-value" id="correctRate">—</span>
            <span class="stat-label">Correct Rate</span>
        </div>
    </div>

    <div class="chart-section">
        <h3>Daily Activity (Last 30 Days)</h3>
        <canvas id="dailyChart" width="400" height="200"></canvas>
    </div>

    <div class="chart-section">
        <h3>Accuracy by Sound</h3>
        <canvas id="phonemeChart" width="400" height="300"></canvas>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"
        integrity="sha384-..." crossorigin="anonymous"></script>
<script src="{% static 'js/dashboard.js' %}"></script>
{% endblock %}
```

### JavaScript

**File: `static/js/dashboard.js`**

```javascript
document.addEventListener('DOMContentLoaded', async () => {
    await loadSummary();
    await loadDailyChart();
    await loadPhonemeChart();
});

async function loadSummary() {
    const resp = await fetch('/api/speech/diagnostics/summary/');
    const data = await resp.json();

    document.getElementById('totalAttempts').textContent = data.total_attempts;
    document.getElementById('avgConfidence').textContent =
        Math.round(data.avg_confidence * 100) + '%';
    document.getElementById('correctRate').textContent =
        Math.round(data.correct_rate * 100) + '%';
}

async function loadDailyChart() {
    const resp = await fetch('/api/speech/diagnostics/daily/');
    const data = await resp.json();

    new Chart(document.getElementById('dailyChart'), {
        type: 'bar',
        data: {
            labels: data.map(d => d.day),
            datasets: [{
                label: 'Attempts',
                data: data.map(d => d.attempts),
                backgroundColor: '#4a90d9',
                borderRadius: 4,
            }],
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 } },
            },
        },
    });
}

async function loadPhonemeChart() {
    const resp = await fetch('/api/speech/diagnostics/phonemes/');
    const data = await resp.json();

    new Chart(document.getElementById('phonemeChart'), {
        type: 'bar',
        data: {
            labels: data.map(d => d.phoneme),
            datasets: [{
                label: 'Correct Rate',
                data: data.map(d => d.correct_rate * 100),
                backgroundColor: '#4CAF50',
                borderRadius: 4,
            }],
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            scales: {
                x: { min: 0, max: 100, title: { display: true, text: '%' } },
            },
        },
    });
}
```

### CSS

**File: `static/css/dashboard.css`**

```css
.dashboard {
    max-width: 900px;
    margin: 0 auto;
}

.stats-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.stat-value {
    display: block;
    font-size: 2rem;
    font-weight: 700;
    color: #4a90d9;
}

.stat-label {
    font-size: 0.875rem;
    color: #888;
}

.chart-section {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

@media (max-width: 767px) {
    .stats-row {
        grid-template-columns: 1fr;
    }
}
```

## Acceptance Criteria

- [ ] Summary stats displayed (total, confidence, correct rate)
- [ ] Daily activity bar chart for last 30 days
- [ ] Per-phoneme accuracy horizontal bar chart
- [ ] Responsive layout at all breakpoints
- [ ] Data fetched from diagnostics API endpoints

## Test Strategy

- Manual: Navigate to `/diagnostics/`, verify charts render
- Manual: With data → charts populated; without data → empty gracefully
- Manual: Responsive at mobile/tablet/desktop
