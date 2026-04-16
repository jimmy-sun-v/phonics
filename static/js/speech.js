function initRepeatStep(phonemeSymbol, sessionId) {
  const micBtn = document.getElementById("micBtn");
  const indicator = document.getElementById("recordingIndicator");
  const feedbackArea = document.getElementById("feedbackArea");
  const feedbackText = document.getElementById("feedbackText");
  const starRating = document.getElementById("starRating");
  const stepNav = document.getElementById("stepNav");
  const retryBtn = document.getElementById("retryBtn");
  const instruction = document.getElementById("instruction");

  let mediaRecorder = null;
  let audioChunks = [];
  let isRecording = false;
  let audioContext = null;

  micBtn.addEventListener("click", toggleRecording);
  retryBtn.addEventListener("click", resetForRetry);

  async function toggleRecording() {
    if (isRecording) {
      stopRecording();
    } else {
      await startRecording();
    }
  }

  async function startRecording() {
    // Clear previous feedback
    feedbackArea.style.display = "none";
    stepNav.style.display = "none";

    try {
      if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
      }
      audioContext.resume();

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { sampleRate: 16000, channelCount: 1 },
      });

      audioChunks = [];
      mediaRecorder = new MediaRecorder(stream, {
        mimeType: "audio/webm;codecs=opus",
      });

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunks.push(e.data);
      };

      mediaRecorder.onstop = () => {
        stream.getTracks().forEach((t) => t.stop());
        processRecording();
      };

      mediaRecorder.start();
      isRecording = true;
      micBtn.classList.add("recording");
      indicator.style.display = "";

      setTimeout(() => {
        if (isRecording) stopRecording();
      }, 3000);
    } catch (err) {
      if (err.name === "NotAllowedError") {
        instruction.textContent = "Please allow microphone access to continue.";
      } else {
        instruction.textContent =
          "Could not access microphone. Please try again.";
      }
    }
  }

  function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
    }
    isRecording = false;
    micBtn.classList.remove("recording");
    indicator.style.display = "none";
  }

  async function processRecording() {
    instruction.textContent = "Thinking...";
    document.getElementById("thinkingAnimation").style.display = "";

    const blob = new Blob(audioChunks, { type: "audio/webm" });
    const reader = new FileReader();

    reader.onload = async () => {
      const base64 = reader.result.split(",")[1];

      try {
        const response = await fetch("/api/speech/attempt/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
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
        feedbackArea.style.display = "";
        stepNav.style.display = "";
      } finally {
        document.getElementById("thinkingAnimation").style.display = "none";
      }
    };

    reader.readAsDataURL(blob);
  }

  function showFeedback(data) {
    feedbackArea.style.display = "";
    feedbackText.textContent = data.feedback || "Good try!";

    const confidence = data.confidence || 0;
    const starCount = confidence >= 80 ? 3 : confidence >= 50 ? 2 : 1;
    starRating.setAttribute("aria-label", starCount + " out of 3 stars");
    for (let i = 1; i <= 3; i++) {
      const el = document.getElementById("star" + i);
      el.className = "star star-empty";
      el.style.animationDelay = "";
      if (i <= starCount) {
        // Force reflow to restart animation
        void el.offsetWidth;
        el.className = "star star-filled";
        el.style.animationDelay = (i - 1) * 0.2 + "s";
      }
    }

    if (typeof setMascotState === "function") {
      setMascotState(data.is_correct ? "happy" : "encouraging");
    }

    stepNav.style.display = "";
    instruction.textContent = data.is_correct
      ? "Great job! 🌟"
      : "Let's try again!";

    playFeedbackAudio(data.feedback || "Good try!");
  }

  async function playFeedbackAudio(text) {
    try {
      const response = await fetch(
        "/api/speech/tts/?text=" + encodeURIComponent(text),
      );
      if (!response.ok) return;
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audio.play().catch(() => {
        // Autoplay blocked — text feedback is already shown
      });
    } catch (e) {
      // TTS unavailable — text feedback is already shown
    }
  }

  function resetForRetry() {
    feedbackArea.style.display = "none";
    stepNav.style.display = "none";
    instruction.textContent = 'Tap and say "' + phonemeSymbol + '"';
  }

  function getCsrfToken() {
    const cookie = document.cookie
      .split(";")
      .find((c) => c.trim().startsWith("csrftoken="));
    return cookie ? cookie.split("=")[1] : "";
  }
}
