import json
import re
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL


class AIService:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

    def ask(self, system_prompt, user_prompt, temperature=0.2):
        if not self.client:
            raise RuntimeError('GROQ_API_KEY is missing. Add it to your .env file.')
        response = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content or ''

    @staticmethod
    def _extract_json(raw):
        text = (raw or '').strip()
        text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.I)
        text = re.sub(r'\s*```$', '', text)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        starts = [i for i in (text.find('{'), text.find('[')) if i >= 0]
        if not starts:
            raise ValueError('The AI returned an invalid JSON response. Please try again.')
        start = min(starts)
        end = max(text.rfind('}'), text.rfind(']'))
        if end <= start:
            raise ValueError('The AI returned an incomplete JSON response. Please try again.')
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError as exc:
            raise ValueError('The AI returned an invalid JSON response. Please try again.') from exc

    def tutor(self, context, question, mode='Ask', language='English'):
        instructions = {
            'Ask': 'Answer the question clearly and directly.',
            'Explain': 'Explain the concept step-by-step with a simple example.',
            'ELI5': 'Explain it in very simple language using an everyday analogy.',
            'Exam': 'Give an exam-friendly explanation with key points and a short answer.',
            'Teach Me': 'Teach the concept interactively: explain, give an example, then ask one short check question.'
        }
        system = (
            f"You are StudyRAG, a study tutor. {instructions.get(mode, instructions['Ask'])}\n"
            f"Use ONLY the supplied PDF context. If it is insufficient, say so. Respond in {language}. Do not invent facts."
        )
        return self.ask(system, f'PDF CONTEXT:\n{context}\n\nSTUDENT QUESTION:\n{question}', 0.2)

    def generate(self, context, kind, count, difficulty='Medium'):
        if kind == 'flashcards':
            system = (
                f'Create exactly {count} concise flashcards from the supplied PDF context. '
                'Use only the context. Return ONLY valid JSON in this exact shape: '
                '{"items":[{"question":"...","answer":"..."}]}.'
            )
        else:
            system = (
                f'Create exactly {count} MCQs from the supplied PDF context at {difficulty} difficulty. '
                'Use only the context. Each question must have exactly 4 options and one correct answer. '
                'Return ONLY valid JSON in this exact shape: '
                '{"items":[{"question":"...","options":["...","...","...","..."],"answer":"..."}]}.'
            )

        raw = self.ask(system, f'PDF CONTEXT:\n{context}', 0.3)
        data = self._extract_json(raw)
        items = data.get('items', []) if isinstance(data, dict) else data
        if not isinstance(items, list):
            raise ValueError('The AI returned an unexpected result format.')

        cleaned = []
        for item in items:
            if not isinstance(item, dict):
                continue
            if kind == 'flashcards':
                question = str(item.get('question', '')).strip()
                answer = str(item.get('answer', '')).strip()
                if question and answer:
                    cleaned.append({'question': question, 'answer': answer})
            else:
                question = str(item.get('question', '')).strip()
                options = item.get('options', [])
                answer = str(item.get('answer', '')).strip()
                if isinstance(options, list):
                    options = [str(x).strip() for x in options if str(x).strip()]
                else:
                    options = []
                if question and len(options) == 4 and answer in options:
                    cleaned.append({'question': question, 'options': options, 'answer': answer})

        if len(cleaned) < count:
            raise ValueError(f'The AI generated only {len(cleaned)} valid items. Please try again.')
        return cleaned[:count]
