function initBlendBuilder(targetWord) {
  const slotsContainer = document.getElementById("wordSlots");
  const bankContainer = document.getElementById("letterBank");
  const letters = targetWord.split("");
  const shuffled = [...letters].sort(() => Math.random() - 0.5);
  let filledSlots = new Array(letters.length).fill(null);
  let selectedTile = null;
  let dragClone = null;
  let dragTileIndex = null;
  let dragSourceTile = null;

  const isTouchDevice =
    "ontouchstart" in window || navigator.maxTouchPoints > 0;

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
    tile.dataset.letter = letter;
    tile.dataset.originalIndex = i;
    tile.tabIndex = 0;
    tile.addEventListener("click", () => selectTile(tile));
    tile.addEventListener("keydown", (e) => {
      if (e.key === "Enter") selectTile(tile);
    });

    if (isTouchDevice) {
      // Mobile: use touch events; disable draggable to prevent native drag
      tile.draggable = false;
      tile.addEventListener("touchstart", (e) => handleTouchStart(e, tile, i), {
        passive: false,
      });
    } else {
      // Desktop: use HTML5 Drag and Drop
      tile.draggable = true;
      tile.addEventListener("dragstart", (e) => {
        e.dataTransfer.setData("text/plain", i.toString());
      });
    }

    bankContainer.appendChild(tile);
  });

  function handleTouchStart(e, tile, tileIndex) {
    if (tile.classList.contains("used")) return;
    e.preventDefault();
    dragTileIndex = tileIndex;
    dragSourceTile = tile;

    // Create a visual clone that follows the finger
    dragClone = tile.cloneNode(true);
    dragClone.style.position = "fixed";
    dragClone.style.pointerEvents = "none";
    dragClone.style.zIndex = "1000";
    dragClone.style.opacity = "0.85";
    dragClone.style.transform = "scale(1.1)";
    dragClone.style.margin = "0";
    var touch = e.touches[0];
    dragClone.style.left = touch.clientX - 30 + "px";
    dragClone.style.top = touch.clientY - 30 + "px";
    document.body.appendChild(dragClone);

    tile.classList.add("selected");

    // Bind move/end on document so they always fire
    document.addEventListener("touchmove", handleTouchMove, {
      passive: false,
    });
    document.addEventListener("touchend", handleTouchEnd, { passive: false });
    document.addEventListener("touchcancel", handleTouchCancel, {
      passive: false,
    });
  }

  function handleTouchMove(e) {
    if (dragClone === null) return;
    e.preventDefault();
    var touch = e.touches[0];
    dragClone.style.left = touch.clientX - 30 + "px";
    dragClone.style.top = touch.clientY - 30 + "px";

    // Highlight the slot under the finger
    var elem = document.elementFromPoint(touch.clientX, touch.clientY);
    slotsContainer.querySelectorAll(".drop-slot").forEach(function (s) {
      s.classList.remove("drag-hover");
    });
    if (elem && elem.classList.contains("drop-slot")) {
      elem.classList.add("drag-hover");
    }
  }

  function handleTouchEnd(e) {
    if (dragClone === null || dragTileIndex === null) {
      cleanupTouch();
      return;
    }
    e.preventDefault();

    // Determine drop target before cleanup
    var touch = e.changedTouches[0];
    var elem = document.elementFromPoint(touch.clientX, touch.clientY);
    var targetSlotIndex = null;
    if (elem && elem.classList.contains("drop-slot")) {
      targetSlotIndex = parseInt(elem.dataset.index);
    }

    var tileIdx = dragTileIndex;
    cleanupTouch();

    if (targetSlotIndex !== null) {
      placeTile(tileIdx, targetSlotIndex);
    }
  }

  function handleTouchCancel() {
    cleanupTouch();
  }

  function cleanupTouch() {
    if (dragClone) {
      dragClone.remove();
      dragClone = null;
    }
    slotsContainer.querySelectorAll(".drop-slot").forEach(function (s) {
      s.classList.remove("drag-hover");
    });
    if (dragSourceTile) {
      dragSourceTile.classList.remove("selected");
      dragSourceTile = null;
    }
    dragTileIndex = null;
    document.removeEventListener("touchmove", handleTouchMove);
    document.removeEventListener("touchend", handleTouchEnd);
    document.removeEventListener("touchcancel", handleTouchCancel);
  }

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
