import time

import pandas as pd
import streamlit as st

from src.answer_generation import build_evidence_answer
from src.chunking import build_chunks
from src.demo_presentation import (
    APP_CSS,
    BOUNDARY_HTML,
    CORPUS_HTML,
    DEFAULT_QUESTION,
    HERO_HTML,
    WORKFLOW_HTML,
)
from src.ingestion import load_documents
from src.retrieval import HybridRetriever


st.set_page_config(
    page_title="Knowledge Retrieval Agent",
    page_icon="🔎",
    layout="wide",
)
st.markdown(APP_CSS, unsafe_allow_html=True)
st.markdown(HERO_HTML, unsafe_allow_html=True)

DATA_DIR = "data/sample_docs"


@st.cache_resource(show_spinner=False)
def load_retriever(chunk_size: int, overlap: int):
    documents = load_documents(DATA_DIR)
    chunks = build_chunks(documents, chunk_size=chunk_size, overlap=overlap)
    retriever = HybridRetriever(chunks)
    return documents, chunks, retriever


st.subheader("Approved knowledge base")
st.write(
    "The public demo searches only three fictional NimbusNote documents. The corpus is intentionally small so the retrieval boundary is easy to inspect."
)
st.markdown(CORPUS_HTML, unsafe_allow_html=True)

st.subheader("How a question moves through the system")
st.markdown(WORKFLOW_HTML, unsafe_allow_html=True)

with st.expander("Engineering controls", expanded=False):
    st.caption("These controls expose the retrieval mechanics without changing the business rule that answers must come from the approved corpus.")
    top_k = st.slider("Top-k evidence chunks", min_value=1, max_value=10, value=5)
    chunk_size = st.slider("Chunk size", min_value=500, max_value=1800, value=900, step=100)
    overlap = st.slider("Chunk overlap", min_value=50, max_value=400, value=150, step=50)
    vector_weight = st.slider("Semantic vector weight", min_value=0.0, max_value=1.0, value=0.65, step=0.05)

with st.status("Preparing approved corpus…", expanded=False) as corpus_status:
    documents, chunks, retriever = load_retriever(chunk_size, overlap)
    corpus_status.update(label="Approved corpus ready", state="complete")

metric_a, metric_b, metric_c = st.columns(3)
metric_a.metric("Approved documents", len(documents))
metric_b.metric("Searchable chunks", len(chunks))
metric_c.metric("Answer boundary", "Corpus only")

st.markdown("---")
st.subheader("Ask the knowledge base")
question = st.text_area(
    "Question",
    value=DEFAULT_QUESTION,
    height=100,
    help="Try policy, support, or security questions that should be answerable from the fictional NimbusNote corpus.",
)
run_button = st.button("Retrieve evidence and answer", type="primary", use_container_width=True)

if run_button:
    if not question.strip():
        st.warning("Please enter a question.")
    elif not chunks:
        st.error("No approved documents were found in the demo corpus.")
    else:
        events = []
        results = []
        evidence = None

        with st.status("Searching the approved corpus…", expanded=True) as retrieval_status:
            for event in retriever.search_iter(question, top_k=top_k, vector_weight=vector_weight):
                events.append(event)
                retrieval_status.write(event["message"])
                if "results" in event:
                    results = event["results"]
                if "evidence" in event:
                    evidence = event["evidence"]
                time.sleep(0.18)

            if evidence and evidence["status"] == "insufficient":
                retrieval_status.update(label="Retrieval finished — evidence gate stopped the answer", state="error", expanded=True)
            else:
                retrieval_status.update(label="Retrieval finished — evidence ranked and checked", state="complete", expanded=False)

        answer = build_evidence_answer(question, results)
        top_result = results[0] if results else None

        st.subheader("Evidence decision")
        if evidence is None:
            st.error("The retrieval pipeline did not produce an evidence assessment.")
        elif evidence["status"] == "sufficient":
            st.success(f"{evidence['label']}: {evidence['reason']}")
        elif evidence["status"] == "limited":
            st.warning(f"{evidence['label']}: {evidence['reason']}")
        else:
            st.error(f"{evidence['label']}: {evidence['reason']}")

        decision_a, decision_b, decision_c = st.columns(3)
        decision_a.metric("Evidence status", evidence["label"] if evidence else "Unknown")
        decision_b.metric("Top source", top_result["source"] if top_result else "None")
        decision_c.metric("Top hybrid score", f"{top_result['hybrid_score']:.3f}" if top_result else "0.000")

        st.subheader("Source-cited answer")
        st.markdown(answer)

        evidence_tab, diagnostics_tab, architecture_tab, evaluation_tab = st.tabs(
            ["Retrieved Evidence", "Retrieval Diagnostics", "Architecture & Limits", "Evaluation"]
        )

        with evidence_tab:
            st.caption("These are the exact approved-corpus chunks used to support or qualify the answer.")
            if not results:
                st.info("No evidence chunks were retrieved.")
            for result in results:
                with st.expander(
                    f"Rank {result['rank']} · {result['source']} · chunk {result['chunk_number']}",
                    expanded=result["rank"] <= 3,
                ):
                    st.write(result["text"])
                    st.caption(
                        f"Semantic {result['vector_score']:.3f} · "
                        f"Keyword {result['keyword_score']:.3f} · "
                        f"Hybrid {result['hybrid_score']:.3f}"
                    )

        with diagnostics_tab:
            diagnostics = pd.DataFrame(
                [
                    {
                        "rank": item["rank"],
                        "source": item["source"],
                        "chunk": item["chunk_number"],
                        "semantic_score": item["vector_score"],
                        "keyword_score": item["keyword_score"],
                        "hybrid_score": item["hybrid_score"],
                    }
                    for item in results
                ]
            )
            st.dataframe(diagnostics, use_container_width=True, hide_index=True)
            st.markdown("**Actual retrieval event trace**")
            for index, event in enumerate(events, start=1):
                st.write(f"{index}. **{event['event']}** — {event['message']}")

        with architecture_tab:
            st.markdown(BOUNDARY_HTML, unsafe_allow_html=True)
            st.markdown(
                """
                **Architecture**
                1. Load approved Markdown/TXT documents.
                2. Build overlapping source-labelled chunks.
                3. Encode the query and corpus with `all-MiniLM-L6-v2`.
                4. Score semantic similarity and BM25 keyword relevance independently.
                5. Combine both signals into a deterministic hybrid score.
                6. Apply an explicit evidence-strength gate.
                7. Build an extractive answer only from retrieved chunks and cite source + chunk.

                **Important limitations**
                - Retrieval relevance does not prove source truth.
                - Character-based chunks can split ideas at imperfect boundaries.
                - The sufficiency thresholds are portfolio-demo policy, not universal calibration.
                - The demo corpus is small and synthetic; production systems need access control, freshness/versioning, larger-scale indexing, and richer evaluation.
                - This agent deliberately does not use an LLM to fill gaps when evidence is weak.
                """
            )

        with evaluation_tab:
            st.markdown(
                """
                The repository includes a synthetic retrieval benchmark covering policy, support, and security questions.

                Production deployment is intended to require:
                - all benchmark questions to retrieve the expected source within the **top 3**, and
                - mean reciprocal rank (**MRR**) of at least **0.75**.

                This evaluates the retrieval primitive itself rather than grading prose style.
                """
            )
else:
    st.info("Run the default enterprise-security question to see the complete evidence-retrieval path.")

st.markdown("---")
st.markdown(BOUNDARY_HTML, unsafe_allow_html=True)
st.caption("Synthetic public-demo corpus only. GitHub is the source of truth; Hugging Face is the hosted demo.")
