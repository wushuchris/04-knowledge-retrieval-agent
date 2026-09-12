from typing import Dict, List

import pandas as pd


def evaluate_retrieval(retriever, eval_path: str, top_k: int = 5) -> pd.DataFrame:
    """Evaluate where the expected source appears in ranked retrieval results."""
    df = pd.read_csv(eval_path)
    rows = []

    for _, row in df.iterrows():
        question = row["question"]
        expected_source = row["expected_source"]
        results = retriever.search(question, top_k=top_k)
        retrieved_sources = [result["source"] for result in results]

        source_rank = next(
            (index for index, source in enumerate(retrieved_sources, start=1) if source == expected_source),
            None,
        )

        rows.append(
            {
                "question": question,
                "expected_source": expected_source,
                "retrieved_sources": "; ".join(retrieved_sources),
                "source_rank": source_rank,
                "hit_at_1": source_rank == 1,
                "hit_at_3": source_rank is not None and source_rank <= 3,
                "reciprocal_rank": 0.0 if source_rank is None else 1.0 / source_rank,
            }
        )

    return pd.DataFrame(rows)


def summarize_retrieval_evaluation(results: pd.DataFrame) -> Dict[str, float]:
    if results.empty:
        return {"cases": 0, "hit_at_1": 0.0, "hit_at_3": 0.0, "mrr": 0.0}

    return {
        "cases": int(len(results)),
        "hit_at_1": float(results["hit_at_1"].mean()),
        "hit_at_3": float(results["hit_at_3"].mean()),
        "mrr": float(results["reciprocal_rank"].mean()),
    }
