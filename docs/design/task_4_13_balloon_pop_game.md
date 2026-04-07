# Design: Task 4.13 – Game – Balloon Pop

## Overview

Build the Balloon Pop game: balloons float up with letters/phonemes, child taps balloons with the correct sound to pop them.

## Dependencies

- Task 3.15 (Games API)
- Task 4.1 (Layout)

## Detailed Design

### URL Route

| URL | View | Template |
|-----|------|----------|
| `/games/balloon_pop/<symbol>/` | `balloon_pop_view` | `games/balloon_pop.html` |

### Game Mechanics

1. Instruction shows which sound to find
2. Balloons appear at the bottom and float upward continuously
3. Each balloon has a letter/phoneme label
4. Tapping the correct balloon → pop animation + sound + score increment
5. Tapping incorrect → balloon wobbles, no pop
6. Game ends after 5 correct pops

### JavaScript Core Logic

**File: `static/js/games/balloon_pop.js`**

```javascript
function initBalloonPop(targetPhoneme, distractors) {
    const gameArea = document.getElementById('gameArea');
    const scoreEl = document.getElementById('score');
    const targetDisplay = document.getElementById('targetPhoneme');
    let score = 0;
    const targetScore = 5;
    let gameActive = true;
    let spawnInterval;

    targetDisplay.textContent = targetPhoneme;

    function spawnBalloon() {
        if (!gameActive) return;

        const isCorrect = Math.random() < 0.35; // ~35% chance of correct
        const label = isCorrect ? targetPhoneme : distractors[Math.floor(Math.random() * distractors.length)];

        const balloon = document.createElement('div');
        balloon.className = 'balloon';
        balloon.textContent = label;
        balloon.dataset.correct = isCorrect;

        // Random horizontal position
        const left = 10 + Math.random() * 70; // 10%-80%
        balloon.style.left = left + '%';

        // Random color
        const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'];
        balloon.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];

        // Float-up animation duration
        const duration = 4 + Math.random() * 3; // 4-7 seconds
        balloon.style.animationDuration = duration + 's';

        balloon.addEventListener('click', () => popBalloon(balloon));
        balloon.addEventListener('touchend', (e) => {
            e.preventDefault();
            popBalloon(balloon);
        });

        gameArea.appendChild(balloon);

        // Remove balloon after it exits viewport
        setTimeout(() => {
            if (balloon.parentNode) balloon.remove();
        }, duration * 1000);
    }

    function popBalloon(balloon) {
        if (!gameActive) return;

        if (balloon.dataset.correct === 'true') {
            balloon.classList.add('popped');
            score++;
            scoreEl.textContent = `⭐ ${score}/${targetScore}`;

            setTimeout(() => balloon.remove(), 300);

            if (score >= targetScore) {
                endGame();
            }
        } else {
            balloon.classList.add('wobble');
            setTimeout(() => balloon.classList.remove('wobble'), 500);
        }
    }

    function endGame() {
        gameActive = false;
        clearInterval(spawnInterval);
        if (typeof flashMascotState === 'function') flashMascotState('happy');

        const overlay = document.createElement('div');
        overlay.className = 'game-complete-overlay';
        overlay.innerHTML = `
            <h2>Amazing! 🎉</h2>
            <p>You popped all the "${targetPhoneme}" balloons!</p>
            <a href="javascript:history.back()" class="btn-primary">Continue</a>
        `;
        gameArea.appendChild(overlay);
    }

    // Spawn balloons every 1.5 seconds
    spawnInterval = setInterval(spawnBalloon, 1500);
    spawnBalloon(); // First one immediately
}
```

### CSS

**File: `static/css/games/balloon_pop.css`**

```css
.balloon-pop-game {
    position: relative;
    width: 100%;
    height: 70vh;
    overflow: hidden;
    background: linear-gradient(to top, #87CEEB 0%, #E0F7FA 100%);
    border-radius: 16px;
}

.balloon {
    position: absolute;
    bottom: -80px;
    width: 60px;
    height: 75px;
    border-radius: 50% 50% 50% 50% / 40% 40% 60% 60%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    font-weight: 700;
    color: white;
    cursor: pointer;
    animation: float-up-balloon linear forwards;
    user-select: none;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
}

.balloon::after {
    content: '△';
    position: absolute;
    bottom: -12px;
    font-size: 0.75rem;
    color: inherit;
}

@keyframes float-up-balloon {
    from { transform: translateY(0); }
    to { transform: translateY(-100vh); }
}

.balloon.popped {
    animation: pop 0.3s ease-out forwards;
}

@keyframes pop {
    0% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.3); opacity: 0.5; }
    100% { transform: scale(0); opacity: 0; }
}

.balloon.wobble {
    animation: wobble 0.3s ease-in-out;
}

.game-complete-overlay {
    position: absolute;
    inset: 0;
    background: rgba(255,255,255,0.9);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    z-index: 10;
}

/* Responsive: balloon size scales */
@media (min-width: 768px) {
    .balloon {
        width: 70px;
        height: 85px;
        font-size: 1.5rem;
    }
}
```

## Acceptance Criteria

- [ ] Balloons animate upward continuously
- [ ] Correct balloon → pop animation + score increase
- [ ] Incorrect → wobble, no pop
- [ ] Game ends after 5 correct pops
- [ ] Touch and mouse input supported
- [ ] Full-width game area, balloon size scales with viewport

## Test Strategy

- Manual: Pop correct balloons → score increases
- Manual: Incorrect balloon → no pop, wobble
- Manual: Game ends at 5 correct
- Manual: Test on mobile touch
