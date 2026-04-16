document.addEventListener("DOMContentLoaded", () => {
  const buttons = document.querySelectorAll(".letter-btn");
  const scoreEl = document.getElementById("score");
  let currentScore = 0;

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => handleSelection(btn));
  });

  function handleSelection(btn) {
    if (
      btn.classList.contains("correct") ||
      btn.classList.contains("incorrect")
    )
      return;

    if (btn.dataset.correct === "true") {
      btn.classList.add("correct");
      currentScore++;
      scoreEl.textContent = "⭐ " + currentScore;
      if (typeof flashMascotState === "function") flashMascotState("happy");
      showGameComplete();
    } else {
      btn.classList.add("incorrect");
      btn.classList.add("wobble");
      setTimeout(() => btn.classList.remove("wobble"), 500);
    }
  }

  function showGameComplete() {
    const container = document.querySelector(".beginning-sound-game");
    const overlay = document.createElement("div");
    overlay.className = "game-complete-overlay";
    overlay.innerHTML =
      "<h2>Great job! &#127881;</h2>" +
      "<p>You found the right sound!</p>" +
      '<a href="javascript:history.back()" class="btn-primary">Continue</a>';
    container.appendChild(overlay);
  }
});
