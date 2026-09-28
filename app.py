import os
from io import BytesIO
from flask import Flask, jsonify, render_template, request
from pypdf import PdfReader
from config import UPLOAD_DIR, MAX_UPLOAD_MB
from services.rag_engine import RAGEngine
from services.ai_service import AIService
from services.quiz_service import QuizService
from services.flashcard_service import FlashcardService
from services.progress_service import ProgressService
from services.study_plan_service import StudyPlanService

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_MB * 1024 * 1024
rag = RAGEngine()
ai = AIService()
progress = ProgressService()
quiz_service = QuizService(ai, rag)
flashcard_service = FlashcardService(ai, rag)
plan_service = StudyPlanService(ai, rag)


def require_doc():
    if not rag.has_document():
        return jsonify({'error': 'Please upload a PDF first.'}), 400
    return None


def retrieved_context(query, top_k=5, limit=9000):
    items = rag.retrieve(query, top_k)
    return items, rag.format_context(items, limit)


@app.route('/')
def index(): return render_template('index.html')

@app.route('/dashboard')
def dashboard(): return render_template('dashboard.html')

@app.route('/tutor')
def tutor(): return render_template('tutor.html')

@app.route('/quiz')
def quiz(): return render_template('quiz.html')

@app.route('/flashcards')
def flashcards(): return render_template('flashcards.html')

@app.route('/progress')
def progress_page(): return render_template('progress.html')

@app.route('/study-plan')
def study_plan(): return render_template('study_plan.html')


@app.route('/api/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No PDF file was uploaded.'}), 400
    file = request.files['file']
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Please choose a PDF file.'}), 400
    try:
        raw = file.read()
        reader = PdfReader(BytesIO(raw))
        pages = [{'page': n, 'text': (page.extract_text() or '').strip()} for n, page in enumerate(reader.pages, 1)]
        if sum(len(page['text']) for page in pages) == 0:
            return jsonify({'error': 'No readable text found. This may be a scanned PDF.'}), 400

        rag.index_document(file.filename, pages)
        path = os.path.join(UPLOAD_DIR, os.path.basename(file.filename))
        with open(path, 'wb') as saved:
            saved.write(raw)
        progress.add_document(file.filename, len(pages), rag.chunk_count())
        return jsonify({'filename': file.filename, 'pages': len(pages), 'chunks': rag.chunk_count(), 'documents': rag.document_count()})
    except Exception as exc:
        return jsonify({'error': f'Could not process PDF: {exc}'}), 500


@app.route('/api/ask', methods=['POST'])
def ask():
    error = require_doc()
    if error: return error
    data = request.get_json(silent=True) or {}
    question = str(data.get('question', '')).strip()
    if not question:
        return jsonify({'error': 'Please enter a question.'}), 400
    try:
        items, context = retrieved_context(question, 5)
        if not context.strip():
            return jsonify({'error': 'I could not find relevant information in the uploaded PDF.'}), 400
        answer = ai.tutor(context, question, data.get('mode', 'Ask'), data.get('language', 'English'))
        sources = [{'filename': x['filename'], 'page': x['page'], 'score': round(x['score'], 3), 'preview': x['text'][:180]} for x in items]
        return jsonify({'answer': answer, 'sources': sources})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/quiz/generate', methods=['POST'])
def quiz_generate():
    error = require_doc()
    if error: return error
    data = request.get_json(silent=True) or {}
    count = int(data.get('count', 5))
    difficulty = data.get('difficulty', 'Medium')
    count = count if count in (5, 10, 15) else 5
    if difficulty not in ('Easy', 'Medium', 'Hard'):
        difficulty = 'Medium'
    try:
        return jsonify({'items': quiz_service.create(count, difficulty), 'difficulty': difficulty})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/quiz/submit', methods=['POST'])
def quiz_submit():
    data = request.get_json(silent=True) or {}
    answers = data.get('answers', [])
    questions = data.get('questions', [])
    difficulty = data.get('difficulty', 'Medium')
    if not isinstance(questions, list) or not isinstance(answers, list):
        return jsonify({'error': 'Invalid quiz submission.'}), 400
    score = 0
    review = []
    for i, question in enumerate(questions):
        selected = answers[i] if i < len(answers) else None
        correct = question.get('answer')
        is_correct = selected == correct
        score += int(is_correct)
        review.append({'question': question.get('question'), 'selected': selected, 'correct': correct, 'is_correct': is_correct})
    progress.add_quiz(score, len(questions), difficulty)
    return jsonify({'score': score, 'total': len(questions), 'percentage': round(score / len(questions) * 100, 1) if questions else 0, 'review': review})


@app.route('/api/flashcards/generate', methods=['POST'])
def flashcards_generate():
    error = require_doc()
    if error: return error
    data = request.get_json(silent=True) or {}
    count = int(data.get('count', 5))
    count = count if count in (5, 10, 15) else 5
    try:
        return jsonify({'items': flashcard_service.create(count)})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/flashcards/review', methods=['POST'])
def flashcard_review():
    data = request.get_json(silent=True) or {}
    known = max(0, int(data.get('known', 0)))
    total = max(0, int(data.get('total', 0)))
    progress.add_flashcard_review(min(known, total), total)
    return jsonify({'message': 'Review saved.'})


@app.route('/api/progress')
def get_progress(): return jsonify(progress.summary())


@app.route('/api/study-plan', methods=['POST'])
def make_plan():
    error = require_doc()
    if error: return error
    data = request.get_json(silent=True) or {}
    try:
        plan = plan_service.create(data.get('exam_date', ''), data.get('hours', '2'), data.get('goals', 'Pass the exam with strong understanding.'))
        progress.add_plan(plan)
        return jsonify(plan)
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/document')
def document():
    return jsonify({'loaded': rag.has_document(), 'documents': rag.documents, 'chunks': rag.chunk_count(), 'pages': rag.page_count()})


@app.route('/api/clear', methods=['POST'])
def clear():
    rag.clear()
    return jsonify({'message': 'Current documents cleared.'})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
