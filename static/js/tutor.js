function escapeHTML(value) {
    const div = document.createElement('div');
    div.textContent = value ?? '';
    return div.innerHTML;
}

async function askTutor() {
    const q = document.getElementById('question').value.trim();
    const answer = document.getElementById('answer');
    const sources = document.getElementById('sources');
    if (!q) {
        answer.classList.remove('hidden');
        answer.textContent = 'Please enter a question.';
        return;
    }
    answer.classList.remove('hidden');
    answer.textContent = 'Thinking...';
    sources.innerHTML = '';

    try {
        const response = await fetch('/api/ask', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({question: q, mode: document.getElementById('mode').value, language: document.getElementById('language').value})
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Could not answer the question.');
        answer.textContent = data.answer;
        sources.innerHTML = '<h3>Sources</h3>' + (data.sources || []).map(x =>
            `<div class="source"><strong>${escapeHTML(x.filename)} · Page ${x.page}</strong><small>${escapeHTML(x.preview)}</small></div>`
        ).join('');
    } catch (error) {
        answer.textContent = 'Error: ' + error.message;
    }
}
