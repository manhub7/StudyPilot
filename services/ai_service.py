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
        """Parse JSON from a reply that may contain markdown fences or extra prose."""
        text = (raw or '').strip()

        # Fast path: pure JSON, optionally inside ```json fences.
        cleaned = re.sub(r'^```(?:json)?\s*', '', text, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*```$', '', cleaned).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Fallback: find the FIRST complete JSON object/array using a
        # balanced scan that ignores braces inside strings.
        start = next((i for i, ch in enumerate(text) if ch in '{['), None)
        if start is None:
            raise ValueError('The AI returned an invalid JSON response. Please try again.')

        depth = 0
        in_string = False
        escape = False
        for i in range(start, len(text)):
            ch = text[i]
            if in_string:
                if escape:
                    escape = False
                elif ch == '\\':
                    escape = True
                elif ch == '"':
                    in_string = False
                continue
            if ch == '"':
                in_string = True
            elif ch in '{[':
                depth += 1
            elif ch in '}]':
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except json.JSONDecodeError as exc:
                        raise ValueError('The AI returned an invalid JSON response. Please try again.') from exc
        raise ValueError('The AI returned an incomplete JSON response. Please try again.')

    def ask_json(self, system_prompt, user_prompt, temperature=0.2, retries=3):
        """Ask for JSON and retry with a stricter nudge if parsing fails."""
        last_error = None
        for _ in range(retries):
            try:
                raw = self.ask(system_prompt, user_prompt, temperature)
                return self._extract_json(raw)
            except ValueError as exc:
                last_error = exc
                user_prompt += (
                    '\n\nIMPORTANT: Your previous reply was not valid JSON. '
                    'Return ONLY the raw JSON object. No markdown code fences, '
                    'no explanation, and no text before or after the JSON.'
                )
        raise last_error

    def tutor(self, context, question, mode='Ask', language='English'):
        instructions = {
            'Ask': 'Answer the question clearly and directly.',
            'Explain': 'Explain the concept step-by-step with a simple example.',
            'ELI5': 'Explain it in very simple language using an everyday analogy.',
            'Exam': 'Give an exam-friendly explanation with key points and a short answer.',
            'Teach Me': 'Teach the concept interactively: explain, give an example, then ask one short check question.'
        }
        system = (
            f"You are StudyPilot, a study tutor. {instructions.get(mode, instructions['Ask'])}\n"
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

        data = self.ask_json(system, f'PDF CONTEXT:\n{context}', 0.3)
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