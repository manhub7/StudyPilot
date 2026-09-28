import json, os
from datetime import datetime
from config import STUDY_DATA_FILE

DEFAULT = {'quiz_attempts': [], 'flashcard_reviews': [], 'study_plans': [], 'documents': []}

class ProgressService:
    def __init__(self): self.data = self._load()
    def _load(self):
        if not os.path.exists(STUDY_DATA_FILE): return DEFAULT.copy()
        try:
            with open(STUDY_DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except Exception: return DEFAULT.copy()
    def save(self):
        os.makedirs(os.path.dirname(STUDY_DATA_FILE), exist_ok=True)
        with open(STUDY_DATA_FILE, 'w', encoding='utf-8') as f: json.dump(self.data, f, indent=2)
    def add_document(self, filename, pages, chunks):
        self.data['documents'].append({'filename':filename,'pages':pages,'chunks':chunks,'date':datetime.now().isoformat()}); self.save()
    def add_quiz(self, score, total, difficulty):
        self.data['quiz_attempts'].append({'score':score,'total':total,'difficulty':difficulty,'date':datetime.now().isoformat()}); self.save()
    def add_flashcard_review(self, known, total):
        self.data['flashcard_reviews'].append({'known':known,'total':total,'date':datetime.now().isoformat()}); self.save()
    def add_plan(self, plan):
        self.data['study_plans'].append({'plan':plan,'date':datetime.now().isoformat()}); self.save()
    def summary(self):
        quizzes=self.data['quiz_attempts']; reviews=self.data['flashcard_reviews']
        total=sum(x['total'] for x in quizzes); correct=sum(x['score'] for x in quizzes)
        return {'quiz_attempts':len(quizzes),'quiz_questions':total,'correct_answers':correct,'accuracy':round(correct/total*100,1) if total else 0,'flashcard_sessions':len(reviews),'documents':len(self.data['documents']),'recent_quizzes':quizzes[-10:][::-1],'recent_flashcards':reviews[-10:][::-1]}
