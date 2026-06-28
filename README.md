---
title: Knowledge Retrieval Agent
emoji: 🔎
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Knowledge Retrieval Agent

A source-cited private document assistant demo using synthetic, public-safe sample documents for the fictional NimbusNote Knowledge Base.

## Purpose

This agent retrieves relevant evidence from a private document collection, ranks the evidence, and produces a conservative source-grounded answer. It is designed to become the knowledge-access layer for later specialized agents and multi-agent systems.

## Agent Pattern

**Retrieve first. Answer second. Cite always.**

The agent does not rely on memory or unsupported generation. It searches a document collection, returns ranked chunks, and answers from retrieved evidence only.

## Core Capabilities

- Markdown and text document ingestion
- Overlapping text chunking
- Sentence-transformer embeddings
- Keyword retrieval with BM25
- Hybrid vector and keyword ranking
- Source-grounded extractive answers
- Evidence panels with citation metadata
- Retrieval diagnostics
- Small retrieval evaluation set

## Architecture

```text
User Question
    ↓
Document Loader
    ↓
Chunking Layer
    ↓
Embedding Model + BM25 Index
    ↓
Hybrid Retriever
    ↓
Top-K Evidence Chunks
    ↓
Grounded Answer Builder
    ↓
Answer + Sources + Diagnostics
```

## Project Structure

```text
04-knowledge-retrieval-agent/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── sample_docs/
├── src/
│   ├── ingestion.py
│   ├── chunking.py
│   ├── retrieval.py
│   ├── answer_generation.py
│   └── evaluation.py
├── eval/
│   ├── test_questions.csv
│   └── run_eval.py
└── .github/
    └── workflows/
        └── sync_to_huggingface.yml
```

## Quickstart

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Evaluation

Run the retrieval evaluation script:

```bash
python eval/run_eval.py
```

The evaluation checks whether the expected source appears in the top-k retrieved results.

## Deployment Standard

GitHub is the source of truth. Hugging Face Spaces should be the hosted demo.

Recommended workflow:

1. Build and test locally.
2. Commit changes to GitHub.
3. Sync to Hugging Face using the GitHub Action.
4. Test the live Space.
5. Update the README with the live demo link.

## Hugging Face Secrets

For GitHub Actions deployment, add these repository secrets:

```text
HF_TOKEN=your_huggingface_write_token
HF_SPACE=your-username/04-knowledge-retrieval-agent
```

## Responsible Use Notes

This is a retrieval assistant, not a truth engine. It can only answer from the documents it has access to. If the retrieved evidence is weak, incomplete, stale, or irrelevant, the answer should be treated as incomplete.

## Reusable Primitive

This agent becomes the knowledge-access layer for later systems, including:

- Research agents
- Verification agents
- Multi-agent analyst teams
- Advisor workflow agents
- Private knowledge copilots
- Evidence-grounded planning systems
