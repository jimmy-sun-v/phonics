# Design: Task 4.7 – Learning Loop – Repeat Step (Speech Input)

## Overview

Build the "Repeat" step: capture audio via browser MediaRecorder API, submit to the speech attempt API, and display AI feedback.

## Dependencies

- Task 3.13 (Speech attempt API)
- Task 4.6 (Observe step — user arrives from here)

## Detailed Design

### URL Route

| URL | View | Template |
|-----|------|----------|
| `/learn/<symbol>/repeat/` | `repeat_step_view` | `learning/repeat.html` |

### Template

**File: `templates/learning/repeat.html`**

```html
{% extends "base.html" %}
{% load static %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/learning.css' %}">
{% endblock %}

{% block content %}
<div class="learning-step repeat-step">
    <div class="step-indicator">
        <span class="step done">Listen</span>
        <span class="step done">See</span>
        <span class="step active">Say</span>
        <span class="step">Play</span>
        <span class="step">Done!</span>
    </div>

    <div class="phoneme-display">
        <span class="phoneme-large">{{ phoneme.symbol }}</span>
    </div>

    <p class="instruction" id="instruction">Tap and say "{{ phoneme.example_words.0 }}"</p>

    <button class="mic-button" id="micBtn" aria-label="Press to record">
        🎤
    </button>
    <div class="recording-indicator" id="recordingIndicator" style="display:none;">
        <span class="pulse-dot"></span> Listening...
    </div>

    <div class="feedback-area" id="feedbackArea" style="display:none;">
        <div class="confidence-bar">
            <div class="confidence-fill" id="confidenceFill"></div>
        </div>
        <p class="feedback-text" id="feedbackText"></p>
    </div>

    <div class="step-nav" id="stepNav" style="display:none;">
        <button class="btn-secondary" id="retryBtn">Try Again</button>
        <a href="{% url 'phonics:learning-practice' phoneme.symbol %}" class="btn-primary" id="nextBtn">
            Next →
        </a>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/speech.js' %}"></script>
<script>
    initRepeatStep('{{ phoneme.symbol }}', '{{ session_id }}');
</script>
{% endblock %}
```

### JavaScript — Speech Recording

**File: `static/js/speech.js`**

```javascript
function initRepeatStep(phonemeSymbol, sessionId) {
    const micBtn = document.getElementById('micBtn');
    const indicator = document.getElementById('recordingIndicator');
    const feedbackArea = document.getElementById('feedbackArea');
    const feedbackText = document.getElementById('feedbackText');
    const confidenceFill = document.getElementById('confidenceFill');
    const stepNav = document.getElementById('stepNav');
    const retryBtn = document.getElementById('retryBtn');
    const instruction = document.getElementById('instruction');

    let mediaRecorder = null;
    let audioChunks = [];
    let isRecording = false;

    micBtn.addEventListener('click', toggleRecording);
    retryBtn.addEventListener('click', resetForRetry);

    async function toggleRecording() {
        if (isRecording) {
            stopRecording();
        } else {
            await startRecording();
        }
    }

    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: { sampleRate: 16000, channelCount: 1 }
            });

            audioChunks = [];
            mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) audioChunks.push(e.data);
            };

            mediaRecorder.onstop = () => {
                stream.getTracks().forEach(t => t.stop());
                processRecording();
            };

            mediaRecorder.start();
            isRecording = true;
            micBtn.classList.add('recording');
            indicator.style.display = '';

            // Auto-stop after 5 seconds
            setTimeout(() => {
                if (isRecording) stopRecording();
            }, 5000);

        } catch (err) {
            if (err.name === 'NotAllowedError') {
                instruction.textContent = 'Please allow microphone access to continue.';
            } else {
                instruction.textContent = 'Could not access microphone. Please try again.';
            }
        }
    }

    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
        }
        isRecording = false;
        micBtn.classList.remove('recording');
        indicator.style.display = 'none';
    }

    async function processRecording() {
        instruction.textContent = 'Thinking...';

        const blob = new Blob(audioChunks, { type: 'audio/webm' });
        const reader = new FileReader();

        reader.onload = async () => {
            const base64 = reader.result.split(',')[1];

            try {
                const response = await fetch('/api/speech/attempt/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken(),
                    },
                    body: JSON.stringify({
                        session_id: sessionId,
                        phoneme: phonemeSymbol,
                        audio: base64,
                    }),
                });

                const data = await response.json();
                showFeedback(data);
            } catch (err) {
                feedbackText.textContent = "Something went wrong. Let's try again!";
                feedbackArea.style.display = '';
                stepNav.style.display = '';
            }
        };

        reader.readAsDataURL(blob);
    }

    function showFeedback(data) {
        feedbackArea.style.display = '';
        feedbackText.textContent = data.feedback;

        const pct = Math.round(data.confidence * 100);
        confidenceFill.style.width = pct + '%';
        confidenceFill.style.backgroundColor = data.is_correct ? '#4CAF50' : '#FF9800';

        // Update mascot state
        if (typeof setMascotState === 'function') {
            setMascotState(data.is_correct ? 'happy' : 'encouraging');
        }

        stepNav.style.display = '';
        instruction.textContent = data.is_correct ? 'Great job! 🌟' : 'Let\'s try again!';
    }

    function resetForRetry() {
        feedbackArea.style.display = 'none';
        stepNav.style.display = 'none';
        instruction.textContent = `Tap and say "${phonemeSymbol}"`;
    }

    function getCsrfToken() {
        const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }
}
```

### CSS (add to `static/css/learning.css`)

```css
/* === Microphone Button === */
.mic-button {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    border: 3px solid #4a90d9;
    background: white;
    font-size: 2.5rem;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
}

.mic-button:hover {
    background: #f0f4ff;
}

.mic-button.recording {
    border-color: #F44336;
    background: #ffebee;
    animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(244, 67, 54, 0.4); }
    50% { box-shadow: 0 0 0 15px rgba(244, 67, 54, 0); }
}

/* === Recording Indicator === */
.recording-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #F44336;
    font-size: 1rem;
}

.pulse-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #F44336;
    animation: pulse-dot 1s ease-in-out infinite;
}

@keyframes pulse-dot {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* === Confidence Bar === */
.confidence-bar {
    width: 100%;
    max-width: 300px;
    height: 12px;
    background: #e0e0e0;
    border-radius: 6px;
    overflow: hidden;
    margin: 0 auto 1rem;
}

.confidence-fill {
    height: 100%;
    border-radius: 6px;
    transition: width 0.5s ease-out;
    width: 0;
}

/* === Feedback Text === */
.feedback-text {
    font-size: 1.25rem;
    color: #333;
    max-width: 400px;
    margin: 0 auto;
}
```

## Acceptance Criteria

- [ ] Microphone permission requested on first use
- [ ] Recording starts/stops with visual indicator (pulse animation)
- [ ] Audio sent to speech attempt API
- [ ] Feedback displayed with confidence bar and mascot state change
- [ ] Retry button resets for another attempt
- [ ] "Next" button proceeds to Practice step
- [ ] Denied microphone → graceful error message

## Test Strategy

- Manual: Tap mic → record → submit → see feedback
- Manual: Deny mic → error message displayed
- Manual: Test on mobile Chrome and Safari
