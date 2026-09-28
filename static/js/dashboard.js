function escapeHTML(value){const div=document.createElement('div');div.textContent=value??'';return div.innerHTML;}
async function load(){
    try{
        const p=await(await fetch('/api/progress')).json();
        document.getElementById('stats').innerHTML=[['Documents',p.documents],['Quiz Attempts',p.quiz_attempts],['Accuracy',p.accuracy+'%'],['Flashcard Sessions',p.flashcard_sessions]].map(x=>`<div class="stat"><strong>${x[1]}</strong><span>${x[0]}</span></div>`).join('');
        const d=await(await fetch('/api/document')).json();
        document.getElementById('documents').innerHTML=d.documents?.length?d.documents.slice().reverse().map(x=>`<div class="listitem"><b>${escapeHTML(x.filename)}</b><br><small>${x.pages} pages · ${x.chunks} chunks</small></div>`).join(''):'<p class="muted">No document loaded yet. Upload one from the home page.</p>';
    }catch(e){document.getElementById('documents').innerHTML='<p class="muted">Could not load dashboard data.</p>';}
}
load();
