from typing import List, Dict
import pandas as pd


def evaluate_retrieval(retriever, eval_path: str, top_k: int = 5) -> pd.DataFrame:
    """Evaluate whether expected source appears in top-k retrieval results."""
    df = pd.read_csv(eval_path)
    rows = []

    for _, row in df.iterrows():
        question = row["question"]
        expected_source = row["expected_source"]
        results = retriever.search(question, top_k=top_k)
        retrieved_sources = [result["source"] for result in results]
        hit = expected_source in retrieved_sources

        rows.append(
            {
                "question": question,
                "expected_source": expected_source,
                "retrieved_sources": "; ".join(retrieved_sources),
                "hit": hit,
            }
        )

    return pd.DataFrame(rows)
