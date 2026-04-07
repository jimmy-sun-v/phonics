# Design: Task 4.12 – Game – Blend Builder (Drag & Drop)

## Overview

Build the Blend Builder game: child drags scattered letter tiles into the correct order to form a word. Uses HTML5 Drag and Drop API with touch polyfill.

## Dependencies

- Task 3.15 (Games API)
- Task 4.1 (Layout)

## Detailed Design

### URL Route

| URL | View | Template |
|-----|------|----------|
| `/games/blend_builder/<symbol>/` | `blend_builder_view` | `games/blend_builder.html` |

### Game Mechanics

1. Target word shown as blank slots (e.g., `_ _ _ _` for "ship")
2. Letter tiles displayed in scrambled order below
3. Child drags tiles into slots (or taps to select + tap slot)
4. Correct order → celebration animation
5. Wrong placement → tile bounces back to original position

### Template Structure

```html
<div class="game-container blend-builder-game">
    <div class="word-slots" id="wordSlots">
        <!-- Generated dynamically: one slot per letter -->
    </div>

    <div class="letter-bank" id="letterBank">
        <!-- Scrambled letter tiles -->
    </div>

    <p class="game-instruction">Drag the letters!</p>
</div>
```

### JavaScript

**File: `static/js/games/blend_builder.js`**

```javascript
function initBlendBuilder(targetWord) {
    const slotsContainer = document.getElementById('wordSlots');
    const bankContainer = document.getElementById('letterBank');
    const letters = targetWord.split('');
    const shuffled = [...letters].sort(() => Math.random() - 0.5);
    let filledSlots = new Array(letters.length).fill(null);

    // Create slots
    letters.forEach((_, i) => {
        const slot = document.createElement('div');
        slot.className = 'drop-slot';
        slot.dataset.index = i;
        slot.addEventListener('dragover', e => e.preventDefault());
        slot.addEventListener('drop', e => handleDrop(e, i));
        // Keyboard support
        slot.tabIndex = 0;
        slot.setAttribute('role', 'button');
        slot.setAttribute('aria-label', `Slot ${i + 1}`);
        slotsContainer.appendChild(slot);
    });

    // Create tiles
    shuffled.forEach((letter, i) => {
        const tile = document.createElement('div');
        tile.className = 'letter-tile';
        tile.textContent = letter;
        tile.draggable = true;
        tile.dataset.letter = letter;
        tile.dataset.originalIndex = i;
        tile.addEventListener('dragstart', e => {
            e.dataTransfer.setData('text/plain', i.toString());
        });
        // Keyboard: click to select
        tile.tabIndex = 0;
        tile.addEventListener('click', () => selectTile(tile));
        tile.addEventListener('keydown', e => {
            if (e.key === 'Enter') selectTile(tile);
        });
        bankContainer.appendChild(tile);
    });

    // Touch support via pointer events
    enableTouchDrag(bankContainer, slotsContainer);

    function handleDrop(e, slotIndex) {
        e.preventDefault();
        const tileIndex = e.dataTransfer.getData('text/plain');
        placeTile(parseInt(tileIndex), slotIndex);
    }

    function placeTile(tileIndex, slotIndex) {
        const tile = bankContainer.children[tileIndex];
        if (!tile || filledSlots[slotIndex] !== null) return;

        const slot = slotsContainer.children[slotIndex];
        filledSlots[slotIndex] = tile.dataset.letter;
        slot.textContent = tile.dataset.letter;
        slot.classList.add('filled');
        tile.classList.add('used');

        checkCompletion();
    }

    function checkCompletion() {
        if (filledSlots.every(s => s !== null)) {
            const result = filledSlots.join('');
            if (result === targetWord) {
                // Celebration!
                document.querySelector('.blend-builder-game').classList.add('complete');
                if (typeof flashMascotState === 'function') flashMascotState('happy');
            } else {
                // Reset - bounce back
                resetSlots();
            }
        }
    }

    function resetSlots() {
        filledSlots = new Array(letters.length).fill(null);
        slotsContainer.querySelectorAll('.drop-slot').forEach(s => {
            s.textContent = '';
            s.classList.remove('filled');
        });
        bankContainer.querySelectorAll('.letter-tile').forEach(t => {
            t.classList.remove('used');
        });
    }
}
```

### CSS

```css
.word-slots {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    margin-bottom: 2rem;
}

.drop-slot {
    width: 60px;
    height: 60px;
    border: 3px dashed #ccc;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    font-weight: 700;
}

.drop-slot.filled {
    border-style: solid;
    border-color: #4a90d9;
    background: #e3f2fd;
}

.letter-bank {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    justify-content: center;
}

.letter-tile {
    width: 60px;
    height: 60px;
    background: #fff;
    border: 2px solid #4a90d9;
    border-radius: 12px;
    font-size: 1.75rem;
    font-weight: 700;
    cursor: grab;
    display: flex;
    align-items: center;
    justify-content: center;
    user-select: none;
    transition: transform 0.2s;
}

.letter-tile:active { cursor: grabbing; }
.letter-tile.used { opacity: 0.3; pointer-events: none; }

/* Mobile: Vertical layout */
@media (max-width: 767px) {
    .blend-builder-game {
        flex-direction: column;
    }
}
```

### Touch Support

For mobile touch drag-and-drop, use a lightweight touch polyfill or implement via `touchstart/touchmove/touchend` events. Alternative: tap-to-select, tap-slot-to-place pattern (more accessible).

## Acceptance Criteria

- [ ] Letter tiles draggable on desktop (mouse) and mobile (touch)
- [ ] Drop zone shows forming word
- [ ] Correct order → celebration; Wrong → tiles bounce back
- [ ] Keyboard accessible: tab + enter
- [ ] Mobile: vertical layout; Desktop: horizontal

## Test Strategy

- Manual: Drag letters into correct order → celebration
- Manual: Test touch drag on mobile device
- Manual: Keyboard tab + enter as alternative
