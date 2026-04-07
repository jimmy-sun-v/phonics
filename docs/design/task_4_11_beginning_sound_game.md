# Design: Task 4.11 – Game – Beginning Sound Selection

## Overview

Build the Beginning Sound game: display a word/picture, child selects the correct beginning sound from 3-4 letter options.

## Dependencies

- Task 3.15 (Games API)
- Task 4.1 (Layout)

## Detailed Design

### URL Route

| URL | View | Template |
|-----|------|----------|
| `/games/beginning_sound/<symbol>/` | `beginning_sound_view` | `games/beginning_sound.html` |

### Game Mechanics

1. Display a word and image prominently
2. Show 3-4 letter/phoneme buttons (1 correct + 2-3 distractors)
3. Child taps the button matching the beginning sound
4. Correct → celebration; Incorrect → gentle redo

### Template Structure

```html
<div class="game-container beginning-sound-game">
    <div class="target-word">
        <img src="..." alt="ship" class="target-image">
        <span class="target-label">ship</span>
    </div>

    <p class="game-instruction">What sound does it start with?</p>

    <div class="letter-options">
        <button class="letter-btn" data-correct="false">s</button>
        <button class="letter-btn" data-correct="true">sh</button>
        <button class="letter-btn" data-correct="false">ch</button>
        <button class="letter-btn" data-correct="false">th</button>
    </div>
</div>
```

### CSS

Letter buttons styled as large, rounded pill buttons (min 48px height). Uses the same correct/incorrect feedback pattern as Task 4.10.

### Distractor Selection Logic (View)

```python
def _get_distractors(target_phoneme, count=3):
    """Get similar-sounding phonemes as distractors."""
    from apps.phonics.models import Phoneme
    return list(
        Phoneme.objects
        .filter(category=target_phoneme.category)
        .exclude(pk=target_phoneme.pk)
        .order_by("?")[:count]
    )
```

## Acceptance Criteria

- [ ] Word/picture displayed prominently
- [ ] 3-4 letter options as large buttons
- [ ] Correct → celebration; Incorrect → gentle redo
- [ ] Responsive at all breakpoints

## Test Strategy

- Manual: Play game, select correct beginning sound
- Manual: Incorrect selection → encouragement
- Manual: Responsive at all breakpoints
