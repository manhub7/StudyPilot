from .ai_service import AIService


class StudyPlanService:
    def __init__(self, ai_service, rag):
        self.ai = ai_service
        self.rag = rag

    def create(self, exam_date, hours, goals):
        retrieved = self.rag.retrieve(
            'topics concepts definitions important exam material',
            min(12, max(1, self.rag.chunk_count()))
        )
        context = self.rag.format_context(retrieved, 10000)
        if not context.strip():
            raise ValueError('I could not find enough study content in the uploaded PDF.')

        system = (
            'Create a practical personalized study plan from the PDF context. '
            'Return ONLY valid JSON in this exact shape: '
            '{"summary":"...","schedule":[{"day":"...","focus":"...","tasks":["..."],"minutes":60}],"tips":["..."]}. '
            'Do not invent PDF topics. Keep the schedule realistic.'
        )
        raw = self.ai.ask(
            system,
            f'Exam date: {exam_date}\nHours per day: {hours}\nStudent goals: {goals}\nPDF CONTEXT:\n{context}',
            0.2,
        )
        data = self.ai.ask_json(system, f'Exam date: {exam_date}\nHours per day: {hours}\nStudent goals: {goals}\nPDF CONTEXT:\n{context}', 0.2)
        if not isinstance(data, dict):
            raise ValueError('The AI returned an invalid study plan.')
        return data
