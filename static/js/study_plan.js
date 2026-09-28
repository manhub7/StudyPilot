function escapeHTML(value) {
    const div = document.createElement('div');
    div.textContent = value ?? '';
    return div.innerHTML;
}

async function makePlan() {
    const box = document.getElementById('plan');
    box.innerHTML = '<p class="muted">Creating your plan...</p>';
    try {
        const response = await fetch('/api/study-plan', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                exam_date: document.getElementById('examDate').value,
                hours: document.getElementById('hours').value,
                goals: document.getElementById('goals').value
            })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Could not create study plan.');
        box.innerHTML = `<h3>${escapeHTML(data.summary || 'Your Study Plan')}</h3>
            <ol>${(data.schedule || []).map(x => `<li><b>${escapeHTML(x.day)}</b> — ${escapeHTML(x.focus)}<br>${(x.tasks || []).map(escapeHTML).join(', ')} · ${escapeHTML(x.minutes || '')} minutes</li>`).join('')}</ol>
            <h3>Tips</h3><ul>${(data.tips || []).map(x => `<li>${escapeHTML(x)}</li>`).join('')}</ul>`;
    } catch (error) {
        box.innerHTML = `<div class="error-box">${escapeHTML(error.message)}</div>`;
    }
}
