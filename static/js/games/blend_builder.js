function initBlendBuilder(targetWord) {
  const slotsContainer = document.getElementById("wordSlots");
  const bankContainer = document.getElementById("letterBank");
  const letters = targetWord.split("");
  const shuffled = [...letters].sort(() => Math.random() - 0.5);
  let filledSlots = new Array(letters.length).fill(null);
  let selectedTile = null;

  // Create slots
  letters.forEach((_, i) => {
    const slot = document.createElement("div");
    slot.className = "drop-slot";
    slot.dataset.index = i;
    slot.addEventListener("dragover", (e) => e.preventDefault());
    slot.addEventListener("drop", (e) => handleDrop(e, i));
    slot.tabIndex = 0;
    slot.setAttribute("role", "button");
    slot.setAttribute("aria-label", "Slot " + (i + 1));
    slot.addEventListener("click", () => handleSlotClick(i));
    slotsContainer.appendChild(slot);
  });

  // Create tiles
  shuffled.forEach((letter, i) => {
    const tile = document.createElement("div");
    tile.className = "letter-tile";
    tile.textContent = letter;
    tile.draggable = true;
    tile.dataset.letter = letter;
    tile.dataset.originalIndex = i;
    tile.addEventListener("dragstart", (e) => {
      e.dataTransfer.setData("text/plain", i.toString());
    });
    tile.tabIndex = 0;
    tile.addEventListener("click", () => selectTile(tile));
    tile.addEventListener("keydown", (e) => {
      if (e.key === "Enter") selectTile(tile);
    });
    bankContainer.appendChild(tile);
  });

  function selectTile(tile) {
    if (tile.classList.contains("used")) return;
    if (selectedTile) selectedTile.classList.remove("selected");
    selectedTile = tile;
    tile.classList.add("selected");
  }

  function handleSlotClick(slotIndex) {
    if (!selectedTile || filledSlots[slotIndex] !== null) return;
    const tileIndex = parseInt(selectedTile.dataset.originalIndex);
    placeTile(tileIndex, slotIndex);
    selectedTile.classList.remove("selected");
    selectedTile = null;
  }

  function handleDrop(e, slotIndex) {
    e.preventDefault();
    const tileIndex = parseInt(e.dataTransfer.getData("text/plain"));
    placeTile(tileIndex, slotIndex);
  }

  function placeTile(tileIndex, slotIndex) {
    const tile = bankContainer.children[tileIndex];
    if (
      !tile ||
      tile.classList.contains("used") ||
      filledSlots[slotIndex] !== null
    )
      return;

    filledSlots[slotIndex] = tile.dataset.letter;
    const slot = slotsContainer.children[slotIndex];
    slot.textContent = tile.dataset.letter;
    slot.classList.add("filled");
    tile.classList.add("used");

    checkCompletion();
  }

  function checkCompletion() {
    if (filledSlots.every((s) => s !== null)) {
      const result = filledSlots.join("");
      if (result === targetWord) {
        document.querySelector(".blend-builder-game").classList.add("complete");
        if (typeof flashMascotState === "function") flashMascotState("happy");
        showGameComplete();
      } else {
        setTimeout(resetSlots, 500);
      }
    }
  }

  function resetSlots() {
    filledSlots = new Array(letters.length).fill(null);
    slotsContainer.querySelectorAll(".drop-slot").forEach((s) => {
      s.textContent = "";
      s.classList.remove("filled");
    });
    bankContainer.querySelectorAll(".letter-tile").forEach((t) => {
      t.classList.remove("used");
      t.classList.remove("selected");
    });
    selectedTile = null;
  }

  function showGameComplete() {
    const container = document.querySelector(".blend-builder-game");
    const overlay = document.createElement("div");
    overlay.className = "game-complete-overlay";
    overlay.innerHTML =
      "<h2>Great job! &#127881;</h2>" +
      "<p>You spelled the word!</p>" +
      '<a href="javascript:history.back()" class="btn-primary">Continue</a>';
    container.appendChild(overlay);
  }
}
