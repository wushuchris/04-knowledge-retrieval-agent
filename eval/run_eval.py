from src.chunking import build_chunks
from src.evaluation import evaluate_retrieval, summarize_retrieval_evaluation
from src.ingestion import load_documents
from src.retrieval import HybridRetriever

DATA_DIR = "data/sample_docs"
EVAL_PATH = "eval/test_questions.csv"

MIN_HIT_AT_3 = 1.0
MIN_MRR = 0.75


if __name__ == "__main__":
    documents = load_documents(DATA_DIR)
    chunks = build_chunks(documents)
    retriever = HybridRetriever(chunks)
    results = evaluate_retrieval(retriever, EVAL_PATH, top_k=5)
    summary = summarize_retrieval_evaluation(results)

    print(results.to_string(index=False))
    print("\nRetrieval benchmark summary:")
    print(summary)

    if summary["hit_at_3"] < MIN_HIT_AT_3 or summary["mrr"] < MIN_MRR:
        raise SystemExit(
            "Retrieval benchmark failed: expected all sources within top 3 and MRR >= 0.75."
        )
