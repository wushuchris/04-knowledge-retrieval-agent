import numpy as np

from src.answer_generation import build_evidence_answer
from src.chunking import build_chunks, chunk_text
from src.retrieval import HybridRetriever, assess_evidence


class FakeEmbeddingModel:
    """Small deterministic embedding stub for retrieval tests."""

    def encode(self, texts, normalize_embeddings=True):
        vectors = []
        for text in texts:
            lower = text.lower()
            vector = np.array(
                [
                    sum(lower.count(term) for term in ["refund", "account", "retention", "policy"]),
                    sum(lower.count(term) for term in ["security", "sso", "audit", "permission"]),
                    sum(lower.count(term) for term in ["support", "password", "escalate", "onboarding"]),
                ],
                dtype=float,
            )
            if not vector.any():
                vector = np.array([0.01, 0.01, 0.01], dtype=float)
            if normalize_embeddings:
                vector = vector / np.linalg.norm(vector)
            vectors.append(vector)
        return np.vstack(vectors)


CHUNKS = [
    {
        "chunk_id": "policy::chunk-1",
        "source": "product_policy_handbook.md",
        "chunk_number": 1,
        "text": "Refund requests follow the product refund policy. Account deletion and retention rules are documented here.",
    },
    {
        "chunk_id": "security::chunk-1",
        "source": "security_faq.md",
        "chunk_number": 1,
        "text": "Enterprise security supports SSO. Admins can review audit logs and document sharing permissions.",
    },
    {
        "chunk_id": "support::chunk-1",
        "source": "customer_support_playbook.md",
        "chunk_number": 1,
        "text": "Support handles password reset issues, enterprise onboarding, and escalation procedures.",
    },
]


def build_test_retriever():
    return HybridRetriever(CHUNKS, embedding_model=FakeEmbeddingModel())


def test_hybrid_retrieval_ranks_expected_source_first():
    results = build_test_retriever().search("Does the service support SSO and audit logs?", top_k=3)

    assert results[0]["source"] == "security_faq.md"
    assert results[0]["rank"] == 1
    assert results[0]["hybrid_score"] >= results[1]["hybrid_score"]


def test_search_iter_emits_real_retrieval_stage_order():
    events = list(build_test_retriever().search_iter("How do I reset a password?", top_k=3))

    assert [event["event"] for event in events] == [
        "query_received",
        "semantic_scored",
        "keyword_scored",
        "hybrid_ranked",
        "evidence_assessed",
    ]
    assert events[-1]["results"][0]["source"] == "customer_support_playbook.md"


def test_search_uses_same_results_as_observable_pipeline():
    retriever = build_test_retriever()
    direct = retriever.search("What is the refund policy?", top_k=3)
    streamed = list(retriever.search_iter("What is the refund policy?", top_k=3))[-1]["results"]

    assert direct == streamed


def test_assess_evidence_requires_minimum_match_strength():
    weak = [{"hybrid_score": 0.10}]
    limited = [{"hybrid_score": 0.30}]
    strong = [{"hybrid_score": 0.70}]

    assert assess_evidence([])["status"] == "insufficient"
    assert assess_evidence(weak)["status"] == "insufficient"
    assert assess_evidence(limited)["status"] == "limited"
    assert assess_evidence(strong)["status"] == "sufficient"


def test_answer_abstains_when_evidence_is_insufficient():
    results = [
        {
            "source": "security_faq.md",
            "chunk_number": 1,
            "text": "SSO is supported.",
            "hybrid_score": 0.10,
        }
    ]

    answer = build_evidence_answer("What is the cafeteria menu?", results)

    assert "Evidence status: Insufficient" in answer
    assert "will not fill the gap" in answer


def test_answer_cites_source_and_chunk_when_evidence_is_sufficient():
    results = [
        {
            "source": "security_faq.md",
            "chunk_number": 2,
            "text": "NimbusNote enterprise security supports SSO for approved identity providers.",
            "hybrid_score": 0.75,
        }
    ]

    answer = build_evidence_answer("Does NimbusNote support SSO?", results)

    assert "Sufficient retrieval match" in answer
    assert "security_faq.md · chunk 2" in answer


def test_empty_corpus_emits_insufficient_evidence_event():
    retriever = HybridRetriever([], embedding_model=FakeEmbeddingModel())
    events = list(retriever.search_iter("anything"))

    assert [event["event"] for event in events] == ["query_received", "evidence_assessed"]
    assert events[-1]["evidence"]["status"] == "insufficient"
    assert events[-1]["results"] == []


def test_chunking_preserves_source_metadata():
    docs = [{"source": "policy.md", "path": "policy.md", "text": "A" * 1200}]
    chunks = build_chunks(docs, chunk_size=500, overlap=100)

    assert len(chunks) >= 3
    assert all(chunk["source"] == "policy.md" for chunk in chunks)
    assert chunks[0]["chunk_id"] == "policy.md::chunk-1"


def test_chunk_text_rejects_invalid_overlap():
    try:
        chunk_text("text", chunk_size=100, overlap=100)
    except ValueError as exc:
        assert "chunk_size must be greater than overlap" in str(exc)
    else:
        raise AssertionError("Expected invalid chunk configuration to be rejected")


def test_top_k_never_exceeds_available_chunks():
    results = build_test_retriever().search("security", top_k=20)
    assert len(results) == len(CHUNKS)
