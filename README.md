# StudyPilot — AI PDF Study Assistant

StudyPilot is a beginner-friendly Retrieval-Augmented Generation (RAG) study app. Upload a text-based PDF, retrieve relevant passages with TF-IDF, and use Groq to study through an AI Tutor, quizzes, flashcards, progress tracking, and study plans.

## Features

- PDF upload and text extraction
- TF-IDF + cosine-similarity retrieval
- AI Tutor modes: Ask, Explain, ELI5, Exam, Teach Me
- English, Simple English, Urdu, and Roman Urdu tutor responses
- AI-generated quizzes with Easy / Medium / Hard difficulty
- Quiz scoring and mistake review
- Interactive flashcards
- Progress dashboard
- Personalized study plans
- Responsive dark study-focused UI

## Project structure

```text
StudyPilot/
├── app.py
├── config.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
├── data/
│   ├── uploads/
│   └── study_data.json
├── services/
│   ├── ai_service.py
│   ├── flashcard_service.py
│   ├── progress_service.py
│   ├── quiz_service.py
│   ├── rag_engine.py
│   └── study_plan_service.py
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   ├── tutor.html
│   ├── quiz.html
│   ├── flashcards.html
│   ├── progress.html
│   └── study_plan.html
└── static/
    ├── css/
    └── js/
```

## Setup

Open the project folder in VS Code and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Add your Groq API key to `.env`:

```env
GROQ_API_KEY=your_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

Run the app:

```powershell
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## How the RAG pipeline works

```text
PDF
 ↓
PyPDF text extraction
 ↓
Text chunks
 ↓
TF-IDF indexing
 ↓
Cosine similarity retrieval
 ↓
Relevant PDF context
 ↓
Groq AI
 ↓
Tutor answer / Quiz / Flashcards / Study Plan
```

## Important beginner note

The app does not force the Groq provider to validate generated JSON. Instead, the application asks the model for JSON and validates/parses the returned text itself. This avoids provider-side JSON validation failures when a model returns a helpful non-JSON sentence.

## Limitations

- Scanned/image-only PDFs need OCR support, which is not included.
- The current document index lives in memory while the Flask app is running.
- A Groq API key is required for AI Tutor, quiz, flashcards, and study-plan generation.
