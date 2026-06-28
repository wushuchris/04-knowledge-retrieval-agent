from src.ingestion import load_documents
from src.chunking import build_chunks
from src.retrieval import HybridRetriever
from src.evaluation import evaluate_retrieval

DATA_DIR = "data/sample_docs"
EVAL_PATH = "eval/test_questions.csv"

if __name__ == "__main__":
    documents = load_documents(DATA_DIR)
    chunks = build_chunks(documents)
    retriever = HybridRetriever(chunks)
    results = evaluate_retrieval(retriever, EVAL_PATH, top_k=5)
    print(results.to_string(index=False))
    print("\nHit rate:", results["hit"].mean())
