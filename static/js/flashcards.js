let cards = [];

function escapeHTML(value) {
    const div = document.createElement('div');
    div.textContent = value ?? '';
    return div.innerHTML;
}

async function generateFlashcards() {
    const box = document.getElementById('cards');
    box.innerHTML = '<p class="muted">Generating cards...</p>';
    try {
        const response = await fetch('/api/flashcards/generate', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({count: Number(document.getElementById('count').value)})
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Could not generate flashcards.');
        cards = data.items || [];
        box.innerHTML = cards.map((c, i) => `
            <div class="flip" onclick="this.classList.toggle('flipped')">
                <div class="flip-inner">
                    <div class="face"><span><small>QUESTION ${i + 1}</small><b>${escapeHTML(c.question)}</b><em>Click to reveal</em></span></div>
                    <div class="face back"><span><small>ANSWER</small><b>${escapeHTML(c.answer)}</b><em>Click to flip back</em></span></div>
                </div>
            </div>`).join('') +
            '<button class="btn primary review-button" onclick="saveReview()">I finished my review</button>';
    } catch (error) {
        box.innerHTML = `<div class="error-box">${escapeHTML(error.message)}</div>`;
    }
}

async function saveReview() {
    const known = prompt('How many cards did you know? Enter a number:', cards.length);
    const number = Number(known);
    if (known === null || !Number.isFinite(number)) return;
    const n = Math.max(0, Math.min(cards.length, Math.floor(number)));
    await fetch('/api/flashcards/review', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({known: n, total: cards.length})
    });
    alert('Review saved!');
}
