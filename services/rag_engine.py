from typing import Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class RAGEngine:
    def __init__(self, chunk_size=1200, overlap=200):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.documents: List[Dict] = []
        self.chunks: List[Dict] = []
        self.vectorizer = None
        self.matrix = None

    def index_document(self, filename, pages):
        self.documents = [d for d in self.documents if d['filename'] != filename]
        self.documents.append({'filename': filename, 'pages': len(pages)})
        self.chunks = [c for c in self.chunks if c['filename'] != filename]

        for page in pages:
            text = (page.get('text') or '').strip()
            if not text:
                continue
            start = 0
            while start < len(text):
                end = start + self.chunk_size
                chunk = text[start:end].strip()
                if chunk:
                    self.chunks.append({'filename': filename, 'page': page['page'], 'text': chunk})
                if end >= len(text):
                    break
                start = end - self.overlap
        self._rebuild()

    def _rebuild(self):
        if not self.chunks:
            self.vectorizer = None
            self.matrix = None
            return
        texts = [c['text'] for c in self.chunks]
        try:
            self.vectorizer = TfidfVectorizer(lowercase=True, stop_words='english', ngram_range=(1, 2), max_features=12000)
            self.matrix = self.vectorizer.fit_transform(texts)
        except ValueError:
            self.vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), max_features=12000)
            self.matrix = self.vectorizer.fit_transform(texts)

    def retrieve(self, query, top_k=5):
        if not self.chunks or self.vectorizer is None:
            return []
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix)[0]
        indexes = scores.argsort()[::-1]
        results = []
        for i in indexes[:top_k]:
            item = self.chunks[i].copy()
            item['score'] = float(scores[i])
            results.append(item)
        return results

    def format_context(self, retrieved, max_characters=9000):
        parts, total = [], 0
        for item in retrieved:
            piece = f"[Document: {item['filename']} | Page {item['page']}]\n{item['text']}\n"
            if total + len(piece) > max_characters:
                break
            parts.append(piece)
            total += len(piece)
        return '\n---\n'.join(parts)

    def clear(self):
        self.documents = []
        self.chunks = []
        self.vectorizer = None
        self.matrix = None

    def has_document(self):
        return bool(self.chunks)

    def chunk_count(self):
        return len(self.chunks)

    def document_count(self):
        return len(self.documents)

    def page_count(self):
        return sum(d['pages'] for d in self.documents)