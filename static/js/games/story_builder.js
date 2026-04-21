function initStoryBuilder(sessionId) {
  const micBtn = document.getElementById("storyMicBtn");
  const storyTrail = document.getElementById("storyTrail");
  const thinking = document.getElementById("thinking");
  const instruction = document.getElementById("storyInstruction");
  const roundIndicator = document.getElementById("roundIndicator");
  const repeatLastBtn = document.getElementById("repeatLastBtn");
  const wholeStoryBtn = document.getElementById("wholeStoryBtn");
  const storyControls = document.getElementById("storyControls");
  const storySummary = document.getElementById("storySummary");
  const summaryText = document.getElementById("summaryText");
  const hearSummaryBtn = document.getElementById("hearSummaryBtn");
  const storyIntro = document.getElementById("storyIntro");

  let mediaRecorder = null;
  let audioChunks = [];
  let isRecording = false;
  let audioContext = null;
  let storySessionId = null;
  let lastLLMResponse = "";
  let allTurns = [];

  const timerBar = document.getElementById("recordTimerBar");
  const timerFill = document.getElementById("recordTimerFill");
  const RECORD_TIME_LIMIT = 30; // seconds
  let recordTimerInterval = null;

  micBtn.addEventListener("click", toggleRecording);
  repeatLastBtn.addEventListener("click", repeatLast);
  wholeStoryBtn.addEventListener("click", hearWholeStory);
  hearSummaryBtn.addEventListener("click", hearSummary);

  // Read the intro text aloud when the game starts
  playTTS(storyIntro.textContent.trim());

  function toggleRecording() {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  }

  async function startRecording() {
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
      micBtn.textContent = "⏹️";
      instruction.textContent = "Listening... Tap to stop.";

      // Show and animate the timer bar
      startRecordTimer();
    } catch (err) {
      if (err.name === "NotAllowedError") {
        instruction.textContent = "Please allow microphone access.";
      } else {
        instruction.textContent = "Could not access microphone.";
      }
    }
  }

  function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
    }
    isRecording = false;
    micBtn.classList.remove("recording");
    micBtn.textContent = "🎤";
    stopRecordTimer();
  }

  function startRecordTimer() {
    timerBar.style.display = "";
    timerFill.style.width = "100%";
    const startTime = Date.now();
    recordTimerInterval = setInterval(() => {
      const elapsed = (Date.now() - startTime) / 1000;
      const remaining = Math.max(0, RECORD_TIME_LIMIT - elapsed);
      const pct = (remaining / RECORD_TIME_LIMIT) * 100;
      timerFill.style.width = pct + "%";
      if (remaining <= 5) {
        timerFill.classList.add("timer-warning");
      }
      if (remaining <= 0) {
        stopRecording();
      }
    }, 200);
  }

  function stopRecordTimer() {
    clearInterval(recordTimerInterval);
    recordTimerInterval = null;
    timerBar.style.display = "none";
    timerFill.style.width = "100%";
    timerFill.classList.remove("timer-warning");
  }

  async function processRecording() {
    micBtn.disabled = true;
    instruction.textContent = "Understanding...";
    thinking.style.display = "";

    const blob = new Blob(audioChunks, { type: "audio/webm" });
    const reader = new FileReader();

    reader.onload = async () => {
      const base64 = reader.result.split(",")[1];

      try {
        // Transcribe the child's speech via STT
        const sttResponse = await fetch("/api/speech/transcribe/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
          },
          body: JSON.stringify({ audio: base64 }),
        });

        const sttData = await sttResponse.json();
        const childText = sttData.is_successful ? sttData.text : null;

        if (!childText) {
          instruction.textContent = "I couldn't hear you. Try again!";
          thinking.style.display = "none";
          micBtn.disabled = false;
          return;
        }

        addBubble("child", childText);
        allTurns.push({ role: "child", text: childText });

        // Send to story API
        instruction.textContent = "Thinking of what happens next...";

        const body = { session_id: sessionId, text: childText };
        if (storySessionId) body.story_session_id = storySessionId;

        const response = await fetch("/api/games/story/turn/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
          },
          body: JSON.stringify(body),
        });

        const data = await response.json();

        if (!response.ok) {
          instruction.textContent = "Something went wrong. Try again!";
          thinking.style.display = "none";
          micBtn.disabled = false;
          return;
        }

        storySessionId = data.story_session_id;
        lastLLMResponse = data.llm_response;
        allTurns.push({ role: "llm", text: data.llm_response });

        addBubble("llm", data.llm_response);
        roundIndicator.textContent =
          "Round " + data.round_number + " of " + data.total_rounds;

        thinking.style.display = "none";
        repeatLastBtn.style.display = "";
        wholeStoryBtn.style.display = "";
        storyIntro.style.display = "none";

        // Auto-play the LLM response via TTS
        await playTTS(data.llm_response);

        if (data.is_complete) {
          showSummary(data.summary);
        } else {
          instruction.textContent =
            "Your turn! Think about what happens next, then tap the mic.";
          micBtn.disabled = false;
        }
      } catch (err) {
        instruction.textContent = "Something went wrong. Try again!";
        thinking.style.display = "none";
        micBtn.disabled = false;
      }
    };

    reader.readAsDataURL(blob);
  }

  function addBubble(role, text) {
    const bubble = document.createElement("div");
    bubble.className = "story-bubble " + role;

    const label = document.createElement("div");
    label.className = "role-label";
    label.textContent = role === "child" ? "You" : "Storyteller";

    const content = document.createElement("div");
    content.textContent = text;

    bubble.appendChild(label);
    bubble.appendChild(content);
    storyTrail.appendChild(bubble);
    storyTrail.scrollTop = storyTrail.scrollHeight;
  }

  async function repeatLast() {
    if (lastLLMResponse) {
      await playTTS(lastLLMResponse);
    }
  }

  async function hearWholeStory() {
    const fullStory = allTurns.map((t) => t.text).join(". ");
    await playTTS(fullStory);
  }

  function showSummary(summary) {
    storyControls.style.display = "none";
    storySummary.style.display = "";

    // Render summary as individual word spans for highlighting
    const text = summary || "What a wonderful story!";
    summaryText.innerHTML = "";
    const parts = text.split(/(\s+)/);
    let wordIndex = 0;
    parts.forEach(function (part) {
      if (/\S/.test(part)) {
        const span = document.createElement("span");
        span.textContent = part;
        span.setAttribute("data-word-index", wordIndex);
        summaryText.appendChild(span);
        wordIndex++;
      } else {
        summaryText.appendChild(document.createTextNode(part));
      }
    });

    if (typeof setMascotState === "function") {
      setMascotState("happy");
    }
  }

  let currentAudio = null;
  let highlightTimers = [];

  async function hearSummary() {
    const text = summaryText.textContent;
    if (!text) return;

    if (currentAudio && !currentAudio.paused) {
      currentAudio.pause();
      currentAudio = null;
      clearHighlights();
      hearSummaryBtn.textContent = "\uD83D\uDD0A Hear it";
      return;
    }

    hearSummaryBtn.textContent = "\u23F3 Loading...";
    hearSummaryBtn.disabled = true;

    try {
      const response = await fetch(
        "/api/speech/tts/with-words/?text=" + encodeURIComponent(text),
      );
      if (!response.ok) {
        hearSummaryBtn.textContent = "\uD83D\uDD0A Hear it";
        hearSummaryBtn.disabled = false;
        return;
      }
      const data = await response.json();
      const audioBytes = atob(data.audio_base64);
      const arr = new Uint8Array(audioBytes.length);
      for (let i = 0; i < audioBytes.length; i++) {
        arr[i] = audioBytes.charCodeAt(i);
      }
      const blob = new Blob([arr], { type: data.content_type });
      const url = URL.createObjectURL(blob);
      currentAudio = new Audio(url);
      await currentAudio.play().catch(() => {});
      hearSummaryBtn.textContent = "\u23F9\uFE0F Stop";
      hearSummaryBtn.disabled = false;

      scheduleHighlights(data.word_boundaries);

      currentAudio.addEventListener("ended", () => {
        hearSummaryBtn.textContent = "\uD83D\uDD0A Hear it";
        currentAudio = null;
        clearHighlights();
      });
    } catch (e) {
      hearSummaryBtn.textContent = "\uD83D\uDD0A Hear it";
      hearSummaryBtn.disabled = false;
    }
  }

  function scheduleHighlights(boundaries) {
    clearHighlights();
    const wordSpans = summaryText.querySelectorAll("span[data-word-index]");
    boundaries.forEach(function (wb, i) {
      const timer = setTimeout(function () {
        wordSpans.forEach(function (s) {
          s.classList.remove("word-highlight");
        });
        if (wordSpans[i]) {
          wordSpans[i].classList.add("word-highlight");
        }
      }, wb.offset_ms);
      highlightTimers.push(timer);
    });
    const last = boundaries[boundaries.length - 1];
    if (last) {
      highlightTimers.push(
        setTimeout(function () {
          wordSpans.forEach(function (s) {
            s.classList.remove("word-highlight");
          });
        }, last.offset_ms + last.duration_ms),
      );
    }
  }

  function clearHighlights() {
    highlightTimers.forEach(function (t) {
      clearTimeout(t);
    });
    highlightTimers = [];
    const wordSpans = summaryText.querySelectorAll("span[data-word-index]");
    wordSpans.forEach(function (s) {
      s.classList.remove("word-highlight");
    });
  }

  async function playTTS(text) {
    try {
      const response = await fetch(
        "/api/speech/tts/?text=" + encodeURIComponent(text),
      );
      if (!response.ok) return;
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      await audio.play().catch(() => {});
    } catch (e) {
      // TTS unavailable — text is still shown
    }
  }

  function getCsrfToken() {
    const cookie = document.cookie
      .split(";")
      .find((c) => c.trim().startsWith("csrftoken="));
    return cookie ? cookie.split("=")[1] : "";
  }
}
