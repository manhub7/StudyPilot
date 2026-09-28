function escapeHTML(value){const div=document.createElement('div');div.textContent=value??'';return div.innerHTML;}
async function loadProgress(){
    try{
        const p=await(await fetch('/api/progress')).json();
        document.getElementById('progress').innerHTML=[['Quiz Attempts',p.quiz_attempts],['Questions Practiced',p.quiz_questions],['Correct Answers',p.correct_answers],['Accuracy',p.accuracy+'%']].map(x=>`<div class="stat"><strong>${x[1]}</strong><span>${x[0]}</span></div>`).join('');
        document.getElementById('recent').innerHTML=p.recent_quizzes.length?p.recent_quizzes.map(x=>`<div class="listitem"><b>${x.score}/${x.total} · ${escapeHTML(x.difficulty)}</b><br><small>${new Date(x.date).toLocaleString()}</small></div>`).join(''):'<p class="muted">No quiz attempts yet.</p>';
    }catch(e){document.getElementById('recent').innerHTML='<p class="muted">Could not load progress.</p>';}
}
loadProgress();
