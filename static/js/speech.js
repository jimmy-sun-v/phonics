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
        feedbackText.textContent = data.feedback || 'Good try!';

        const confidence = data.confidence || 0;
        const pct = Math.round(confidence * 100);
        confidenceFill.style.width = pct + '%';
        confidenceFill.style.backgroundColor = data.is_correct ? '#4CAF50' : '#FF9800';

        if (typeof setMascotState === 'function') {
            setMascotState(data.is_correct ? 'happy' : 'encouraging');
        }

        stepNav.style.display = '';
        instruction.textContent = data.is_correct ? 'Great job! 🌟' : "Let's try again!";
    }

    function resetForRetry() {
        feedbackArea.style.display = 'none';
        stepNav.style.display = 'none';
        instruction.textContent = 'Tap and say "' + phonemeSymbol + '"';
    }

    function getCsrfToken() {
        const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }
}
