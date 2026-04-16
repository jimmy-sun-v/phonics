document.addEventListener("DOMContentLoaded", () => {
  const cards = document.querySelectorAll(".picture-card");
  const playBtn = document.getElementById("playSound");
  const scoreEl = document.getElementById("score");
  let currentScore = 0;

  playBtn.addEventListener("click", playTargetSound);
  playTargetSound();

  cards.forEach((card) => {
    card.addEventListener("click", () => handleSelection(card));
  });

  function playTargetSound() {
    const correctCard = document.querySelector('[data-correct="true"]');
    if (!correctCard) return;
    const word = correctCard.dataset.word;
    const audio = new Audio(
      "/api/speech/tts/?text=" + encodeURIComponent(word),
    );
    audio.play().catch(() => {});
  }

  function handleSelection(card) {
    if (
      card.classList.contains("correct") ||
      card.classList.contains("incorrect")
    )
      return;

    if (card.dataset.correct === "true") {
      card.classList.add("correct");
      currentScore++;
      scoreEl.textContent = "⭐ " + currentScore;
      if (typeof flashMascotState === "function") flashMascotState("happy");
      showGameComplete();
    } else {
      card.classList.add("incorrect");
      card.classList.add("wobble");
      setTimeout(() => card.classList.remove("wobble"), 500);
    }
  }

  function showGameComplete() {
    const container = document.querySelector(".game-container");
    const overlay = document.createElement("div");
    overlay.className = "game-complete-overlay";
    overlay.innerHTML =
      "<h2>Great job! &#127881;</h2>" +
      "<p>You picked the right picture!</p>" +
      '<a href="javascript:history.back()" class="btn-primary">Continue</a>';
    container.appendChild(overlay);
  }
});
