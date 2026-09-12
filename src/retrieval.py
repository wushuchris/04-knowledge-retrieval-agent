from collections.abc import Iterator
from typing import Dict, List

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def tokenize(text: str) -> List[str]:
    return text.lower().split()


def assess_evidence(results: List[Dict]) -> Dict:
    """Classify retrieval strength without claiming that retrieved text is true."""
    if not results:
        return {
            "status": "insufficient",
            "label": "Insufficient evidence",
            "reason": "No chunks were retrieved from the approved corpus.",
            "top_score": 0.0,
        }

    top_score = float(results[0].get("hybrid_score", 0.0))
    if top_score < 0.25:
        return {
            "status": "insufficient",
            "label": "Insufficient evidence",
            "reason": "The strongest retrieved chunk is too weakly matched to support an answer.",
            "top_score": top_score,
        }
    if top_score < 0.40:
        return {
            "status": "limited",
            "label": "Limited evidence",
            "reason": "Relevant material was retrieved, but the match is weak enough that the answer should be qualified.",
            "top_score": top_score,
        }
    return {
        "status": "sufficient",
        "label": "Sufficient retrieval evidence",
        "reason": "The approved corpus contains a strong retrieval match for this question.",
        "top_score": top_score,
    }


class HybridRetriever:
    """Hybrid vector and keyword retriever for source-grounded RAG."""

    def __init__(
        self,
        chunks: List[Dict],
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        embedding_model=None,
    ):
        self.chunks = chunks
        self.embedding_model_name = embedding_model_name
        self.model = embedding_model or SentenceTransformer(embedding_model_name)
        self.texts = [chunk["text"] for chunk in chunks]
        self.tokenized_texts = [tokenize(text) for text in self.texts]
        self.bm25 = BM25Okapi(self.tokenized_texts) if self.texts else None
        self.embeddings = self.model.encode(self.texts, normalize_embeddings=True) if self.texts else np.array([])

    def search_iter(self, query: str, top_k: int = 5, vector_weight: float = 0.65) -> Iterator[Dict]:
        """Yield real stages from the hybrid retrieval pipeline."""
        clean_query = query.strip()
        yield {
            "event": "query_received",
            "message": "Question accepted. Searching only the approved document corpus.",
            "query": clean_query,
        }

        if not self.chunks:
            evidence = assess_evidence([])
            yield {
                "event": "evidence_assessed",
                "message": evidence["reason"],
                "results": [],
                "evidence": evidence,
            }
            return

        query_embedding = self.model.encode([clean_query], normalize_embeddings=True)
        vector_scores = cosine_similarity(query_embedding, self.embeddings)[0]
        yield {
            "event": "semantic_scored",
            "message": f"Semantic similarity scored across {len(self.chunks)} corpus chunk(s).",
        }

        bm25_scores = np.array(self.bm25.get_scores(tokenize(clean_query)), dtype=float)
        if bm25_scores.max() > bm25_scores.min():
            bm25_scores = (bm25_scores - bm25_scores.min()) / (bm25_scores.max() - bm25_scores.min())
        else:
            bm25_scores = np.zeros_like(bm25_scores)
        yield {
            "event": "keyword_scored",
            "message": "Keyword relevance scored with BM25 and normalized for hybrid ranking.",
        }

        hybrid_scores = (vector_weight * vector_scores) + ((1 - vector_weight) * bm25_scores)
        ranked_indices = np.argsort(hybrid_scores)[::-1][: min(top_k, len(self.chunks))]

        results = []
        for rank, idx in enumerate(ranked_indices, start=1):
            record = dict(self.chunks[idx])
            record["rank"] = rank
            record["vector_score"] = float(vector_scores[idx])
            record["keyword_score"] = float(bm25_scores[idx])
            record["hybrid_score"] = float(hybrid_scores[idx])
            results.append(record)

        yield {
            "event": "hybrid_ranked",
            "message": f"Vector and keyword signals combined; top {len(results)} evidence chunk(s) ranked.",
            "results": results,
        }

        evidence = assess_evidence(results)
        yield {
            "event": "evidence_assessed",
            "message": evidence["reason"],
            "results": results,
            "evidence": evidence,
        }

    def search(self, query: str, top_k: int = 5, vector_weight: float = 0.65) -> List[Dict]:
        final_results: List[Dict] = []
        for event in self.search_iter(query, top_k=top_k, vector_weight=vector_weight):
            if "results" in event:
                final_results = event["results"]
        return final_results
