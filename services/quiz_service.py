class QuizService:
    def __init__(self, ai_service, rag):
        self.ai = ai_service
        self.rag = rag

def create(self, count=5):
    if not self.rag.has_document():
        raise ValueError('Please upload a PDF before generating flashcards.')
    retrieved = self.rag.retrieve(
        'important concepts definitions key facts formulas processes examples',
        min(15, max(1, self.rag.chunk_count()))
    )
    if not retrieved:
        retrieved = self.rag.chunks[:15]
    if not retrieved:
        raise ValueError('I could not find enough useful information in the uploaded PDF.')
    return self.ai.generate(self.rag.format_context(retrieved, 12000), 'flashcards', count)