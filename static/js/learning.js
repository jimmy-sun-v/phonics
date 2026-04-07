function initListenStep(phoneme, exampleWord) {
    const listenBtn = document.getElementById('listenBtn');
    const againBtn = document.getElementById('listenAgainBtn');
    const nextBtn = document.getElementById('nextBtn');
    let hasListened = false;

    function playSound() {
        const text = exampleWord || phoneme;
        const audio = new Audio('/api/speech/tts/?text=' + encodeURIComponent(text));
        audio.play().then(() => {
            if (!hasListened) {
                hasListened = true;
                againBtn.style.display = '';
                nextBtn.style.display = '';
            }
        }).catch(err => {
            console.warn('Autoplay blocked:', err);
            // Still show controls in case audio can't autoplay
            againBtn.style.display = '';
            nextBtn.style.display = '';
        });
    }

    listenBtn.addEventListener('click', playSound);
    againBtn.addEventListener('click', playSound);
}
