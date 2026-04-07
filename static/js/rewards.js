document.addEventListener('DOMContentLoaded', () => {
    if (typeof setMascotState === 'function') {
        setMascotState('happy');
    }

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
