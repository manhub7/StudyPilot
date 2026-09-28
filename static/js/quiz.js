let questions = [];
let difficulty = 'Medium';

function escapeHTML(value) {
    const div = document.createElement('div');
    div.textContent = value ?? '';
    return div.innerHTML;
}

async function generateQuiz() {
    const area = document.getElementById('quizArea');
    area.innerHTML = '<p class="muted loading-text">Generating your quiz...</p>';
    difficulty = document.getElementById('difficulty').value;

    try {
        const response = await fetch('/api/quiz/generate', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({count: Number(document.getElementById('count').value), difficulty})
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Could not generate quiz.');
        questions = data.items || [];
        if (!questions.length) throw new Error('No questions were generated. Please try again.');

        area.innerHTML = questions.map((q, i) => `
            <div class="quiz-card">
                <h3>Question ${i + 1}</h3>
                <p>${escapeHTML(q.question)}</p>
                ${q.options.map((option, index) => `
                    <label class="option">
                        <input type="radio" name="q${i}" value="${encodeURIComponent(option)}">
                        <span>${String.fromCharCode(65 + index)}.</span> ${escapeHTML(option)}
                    </label>`).join('')}
            </div>
        `).join('') + '<button class="btn primary submit-quiz" onclick="submitQuiz()">Submit Quiz</button>';
    } catch (error) {
        area.innerHTML = `<div class="error-box">${escapeHTML(error.message)}</div>`;
    }
}

async function submitQuiz() {
    const answers = questions.map((q, i) => {
        const selected = document.querySelector(`input[name=q${i}]:checked`);
        return selected ? decodeURIComponent(selected.value) : null;
    });

    try {
        const response = await fetch('/api/quiz/submit', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({questions, answers, difficulty})
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Could not submit quiz.');

        document.getElementById('quizArea').innerHTML = `
            <div class="score">${data.score}/${data.total} · ${data.percentage}%</div>
            ${data.review.map(x => `
                <div class="quiz-card">
                    <b class="${x.is_correct ? 'result-correct' : 'result-wrong'}">${x.is_correct ? '✓ Correct' : '✗ Review'}</b>
                    <p>${escapeHTML(x.question)}</p>
                    <small>Your answer: ${escapeHTML(x.selected || 'Not answered')}<br>Correct: ${escapeHTML(x.correct || '')}</small>
                </div>`).join('')}
        `;
    } catch (error) {
        document.getElementById('quizArea').innerHTML = `<div class="error-box">${escapeHTML(error.message)}</div>`;
    }
}
