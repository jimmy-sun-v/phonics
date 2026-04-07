function initBalloonPop(targetPhoneme, distractors) {
    const gameArea = document.getElementById('gameArea');
    const scoreEl = document.getElementById('score');
    let score = 0;
    const targetScore = 5;
    let gameActive = true;
    let spawnInterval;

    function spawnBalloon() {
        if (!gameActive) return;

        const isCorrect = Math.random() < 0.35;
        const label = isCorrect ? targetPhoneme : distractors[Math.floor(Math.random() * distractors.length)];

        const balloon = document.createElement('div');
        balloon.className = 'balloon';
        balloon.textContent = label;
        balloon.dataset.correct = isCorrect;

        const left = 10 + Math.random() * 70;
        balloon.style.left = left + '%';

        const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'];
        balloon.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];

        const duration = 4 + Math.random() * 3;
        balloon.style.animationDuration = duration + 's';

        balloon.addEventListener('click', () => popBalloon(balloon));
        balloon.addEventListener('touchend', (e) => {
            e.preventDefault();
            popBalloon(balloon);
        });

        gameArea.appendChild(balloon);

        setTimeout(() => {
            if (balloon.parentNode) balloon.remove();
        }, duration * 1000);
    }

    function popBalloon(balloon) {
        if (!gameActive || balloon.classList.contains('popped')) return;

        if (balloon.dataset.correct === 'true') {
            balloon.classList.add('popped');
            score++;
            scoreEl.textContent = '⭐ ' + score + '/' + targetScore;

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
        overlay.innerHTML = '<h2>Amazing! &#127881;</h2>' +
            '<p>You popped all the "' + targetPhoneme + '" balloons!</p>' +
            '<a href="javascript:history.back()" class="btn-primary">Continue</a>';
        gameArea.appendChild(overlay);
    }

    spawnInterval = setInterval(spawnBalloon, 1500);
    spawnBalloon();
}
