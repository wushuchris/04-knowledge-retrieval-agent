from typing import List, Dict
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def tokenize(text: str) -> List[str]:
    return text.lower().split()


class HybridRetriever:
    """Hybrid vector and keyword retriever for source-grounded RAG."""

    def __init__(self, chunks: List[Dict], embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.chunks = chunks
        self.embedding_model_name = embedding_model_name
        self.model = SentenceTransformer(embedding_model_name)
        self.texts = [chunk["text"] for chunk in chunks]
        self.tokenized_texts = [tokenize(text) for text in self.texts]
        self.bm25 = BM25Okapi(self.tokenized_texts) if self.texts else None
        self.embeddings = self.model.encode(self.texts, normalize_embeddings=True) if self.texts else np.array([])

    def search(self, query: str, top_k: int = 5, vector_weight: float = 0.65) -> List[Dict]:
        if not self.chunks:
            return []

        query_embedding = self.model.encode([query], normalize_embeddings=True)
        vector_scores = cosine_similarity(query_embedding, self.embeddings)[0]

        bm25_scores = np.array(self.bm25.get_scores(tokenize(query)))
        if bm25_scores.max() > bm25_scores.min():
            bm25_scores = (bm25_scores - bm25_scores.min()) / (bm25_scores.max() - bm25_scores.min())
        else:
            bm25_scores = np.zeros_like(bm25_scores)

        hybrid_scores = (vector_weight * vector_scores) + ((1 - vector_weight) * bm25_scores)
        ranked_indices = np.argsort(hybrid_scores)[::-1][:top_k]

        results = []
        for rank, idx in enumerate(ranked_indices, start=1):
            record = dict(self.chunks[idx])
            record["rank"] = rank
            record["vector_score"] = float(vector_scores[idx])
            record["keyword_score"] = float(bm25_scores[idx])
            record["hybrid_score"] = float(hybrid_scores[idx])
            results.append(record)

        return results
