import streamlit as st
import pandas as pd

from src.ingestion import load_documents
from src.chunking import build_chunks
from src.retrieval import HybridRetriever
from src.answer_generation import build_evidence_answer

st.set_page_config(
    page_title="Knowledge Retrieval Agent",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 Knowledge Retrieval Agent")
st.caption("A source-cited private document assistant using chunking, embeddings, hybrid retrieval, and grounded evidence display.")

DATA_DIR = "data/sample_docs"


@st.cache_resource(show_spinner=True)
def load_retriever(chunk_size: int, overlap: int):
    documents = load_documents(DATA_DIR)
    chunks = build_chunks(documents, chunk_size=chunk_size, overlap=overlap)
    retriever = HybridRetriever(chunks)
    return documents, chunks, retriever


with st.sidebar:
    st.header("Retrieval Settings")
    top_k = st.slider("Top-k chunks", min_value=1, max_value=10, value=5)
    chunk_size = st.slider("Chunk size", min_value=500, max_value=1800, value=900, step=100)
    overlap = st.slider("Chunk overlap", min_value=50, max_value=400, value=150, step=50)
    vector_weight = st.slider("Vector weight", min_value=0.0, max_value=1.0, value=0.65, step=0.05)

    st.markdown("---")
    st.markdown("**Design rule:** The agent should answer from retrieved evidence only.")


documents, chunks, retriever = load_retriever(chunk_size, overlap)

col_a, col_b, col_c = st.columns(3)
col_a.metric("Documents", len(documents))
col_b.metric("Chunks", len(chunks))
col_c.metric("Corpus", DATA_DIR)

st.markdown("---")

question = st.text_input(
    "Ask a question about the private document collection",
    value="What is the purpose of the Knowledge Retrieval Agent?",
)

if st.button("Retrieve and Answer", type="primary"):
    if not question.strip():
        st.warning("Please enter a question.")
    elif not chunks:
        st.error("No documents were found. Add .md or .txt files to data/sample_docs.")
    else:
        results = retriever.search(question, top_k=top_k, vector_weight=vector_weight)
        answer = build_evidence_answer(question, results)

        st.subheader("Source-Grounded Answer")
        st.markdown(answer)

        st.subheader("Retrieved Evidence")
        for result in results:
            with st.expander(
                f"Rank {result['rank']} | {result['source']} | Chunk {result['chunk_number']} | Score {result['hybrid_score']:.3f}",
                expanded=result["rank"] <= 3,
            ):
                st.write(result["text"])
                st.caption(
                    f"Vector score: {result['vector_score']:.3f} | "
                    f"Keyword score: {result['keyword_score']:.3f} | "
                    f"Hybrid score: {result['hybrid_score']:.3f}"
                )

        st.subheader("Retrieval Diagnostics")
        diagnostics = pd.DataFrame(
            [
                {
                    "rank": item["rank"],
                    "source": item["source"],
                    "chunk": item["chunk_number"],
                    "vector_score": item["vector_score"],
                    "keyword_score": item["keyword_score"],
                    "hybrid_score": item["hybrid_score"],
                }
                for item in results
            ]
        )
        st.dataframe(diagnostics, use_container_width=True)
else:
    st.info("Enter a question, then click Retrieve and Answer.")

st.markdown("---")
st.caption("Agent 4 in the Agent Engineering Master Curriculum. GitHub should remain the source of truth; Hugging Face should be the hosted demo.")
