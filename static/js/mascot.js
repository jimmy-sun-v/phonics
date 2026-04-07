/**
 * Update the mascot's visual state.
 * @param {'idle'|'happy'|'encouraging'} state
 */
function setMascotState(state) {
    const mascots = document.querySelectorAll('.mascot');
    const validStates = ['idle', 'happy', 'encouraging'];

    if (!validStates.includes(state)) return;

    mascots.forEach(el => {
        validStates.forEach(s => el.classList.remove(`mascot--${s}`));
        el.classList.add(`mascot--${state}`);
    });
}

/**
 * Briefly show a state, then return to idle.
 * @param {'happy'|'encouraging'} state
 * @param {number} durationMs
 */
function flashMascotState(state, durationMs = 2000) {
    setMascotState(state);
    setTimeout(() => setMascotState('idle'), durationMs);
}
