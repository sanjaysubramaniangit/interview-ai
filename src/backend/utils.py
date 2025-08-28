import fitz
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Read a PDF from bytes and return all text (page by page)."""
    text = ""
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return " ".join(text.split())  # collapse whitespace


def chunk_text(text: str, max_chars: int = 1000, overlap: int = 100) -> List[str]:
    """Split long text into overlapping chunks so retrieval is more precise."""
    chunks = []
    i = 0
    n = len(text)
    while i < n:
        chunk = text[i:i + max_chars]
        chunks.append(chunk)
        if i + max_chars >= n:
            break
        i += max_chars - overlap
    return chunks


class SimpleRAG:
    """
    Tiny RAG helper that:
    - fits a TF-IDF vectorizer on chunks
    - computes cosine similarity for queries
    """
    def __init__(self):
        self.vectorizer = None
        self.doc_matrix = None
        self.chunks = []

    def build(self, chunks: List[str]):
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.doc_matrix = self.vectorizer.fit_transform(chunks)

    def top_k(self, query: str, k: int = 5) -> List[Tuple[int, float]]:
        if not self.vectorizer or not self.doc_matrix or not self.chunks:
            return []
        q_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(q_vec, self.doc_matrix)[0]
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return ranked[:k]

    def context_for(self, query: str, k: int = 5, max_chars: int = 1500) -> str:
        picks = self.top_k(query, k=k)
        pieces = []
        size = 0
        for idx, score in picks:
            piece = self.chunks[idx]
            pieces.append(piece)
            size += len(piece)
            if size >= max_chars:
                break
        return "\n---\n".join(pieces)
