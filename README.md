---
title: Knowledge Retrieval Agent
emoji: 🔎
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Knowledge Retrieval Agent — Approved-Corpus Evidence Retrieval

A production-validated retrieval agent that answers from an approved synthetic knowledge base, exposes how evidence was ranked, and abstains when the retrieved evidence is too weak.

**Live demo:** https://huggingface.co/spaces/FlyingNunchucks/04-knowledge-retrieval-agent

## Business Question

> **How do you make AI answer from approved knowledge instead of from memory — and show the evidence it used?**

The demo uses a fictional NimbusNote support, policy, and security corpus. The business-facing experience starts with the approved sources, then shows the retrieval process, the evidence-strength decision, the source-cited answer, and the exact ranked chunks underneath.

## Agent Pattern

> **Approved corpus → Retrieve → Rank → Assess evidence → Answer or abstain**

The agent does not treat retrieval as automatic permission to answer. A result can be highly ranked relative to other chunks and still be too weak to support a useful response.

## Core Capabilities

- Markdown and text ingestion from an approved document directory
- Overlapping chunk construction with stable source/chunk metadata
- Sentence-transformer semantic retrieval
- BM25 lexical retrieval
- Hybrid semantic + keyword ranking
- Explicit evidence-strength classification
- Source-cited extractive answers
- Explicit abstention when evidence is insufficient
- Real retrieval-stage observability through `search_iter()`
- Ranked evidence panels and engineering diagnostics
- Deterministic retrieval benchmark with Hit@1, Hit@3, and MRR
- Streamlit application smoke testing
- GitHub Actions deployment gated on both tests and retrieval quality

## Architecture

```text
Approved NimbusNote corpus
        ↓
Document ingestion
        ↓
Overlapping chunks + source metadata
        ↓
Semantic scoring + BM25 keyword scoring
        ↓
Hybrid ranking
        ↓
Evidence-strength gate
        ↓
Strong enough? ── No ──> Abstain
        │
       Yes
        ↓
Source-cited extractive answer
        ↓
Ranked evidence + retrieval diagnostics
```

## Observable Retrieval Primitive

`HybridRetriever.search_iter()` exposes the real retrieval pipeline rather than a presentation-only animation.

The live app consumes the same stages used by the normal `search()` API:

1. semantic scoring
2. keyword scoring
3. hybrid ranking
4. evidence-strength assessment
5. final ranked result set

`search()` remains the ordinary convenience API and consumes the iterator internally, so there is no separate demo-only retrieval path.

## Evidence Boundary

A central lesson of Agent 4 is:

> **Retrieval ranking is not permission to answer.**

The answer layer checks the strongest retrieved evidence before producing a response. If the evidence does not cross the configured sufficiency boundary, the agent explicitly says the approved corpus does not contain enough support.

This reduces the temptation to turn a weak nearest-neighbor match into a polished but poorly grounded answer.

## Important Limitation

Agent 4 is a **retrieval system, not a truth-verification system**.

A high retrieval score means:

> “This source chunk is relevant to the question relative to the indexed corpus.”

It does **not** mean:

> “This statement is independently true.”

That distinction becomes the later portfolio handoff into document provenance and evidence verification.

## Evaluation

The project includes an eight-question synthetic retrieval benchmark covering product policy, support operations, and security guidance.

The benchmark records:

- expected source rank
- Hit@1
- Hit@3
- reciprocal rank
- mean reciprocal rank (MRR)

Final approved production result:

- **16 automated tests passed**
- **8/8 expected sources appeared within the top 3**
- **Hit@1 = 87.5%**
- **Hit@3 = 100%**
- **MRR = 0.9375**
- Streamlit application smoke test passed
- Hugging Face deployment succeeded
- final live presentation review approved

Run the deterministic suite:

```bash
python -m pytest -q
```

Run the retrieval benchmark:

```bash
python -m eval.run_eval
```

The GitHub Action must pass both before the `main` branch is deployed to Hugging Face.

## Presentation Retrofit

The original demo led with retrieval tuning controls and raw scores. The approved retrofit reorganized the experience around the business trust model:

- centered **1080px** reading width
- approved corpus shown before the answer
- fictional enterprise-security question as the default scenario
- visible real retrieval stages
- evidence-strength status before answer publication
- source-cited answer followed by inspectable chunks
- engineering controls kept secondary
- explicit reminder that relevance is not independent truth certification

Presentation principle:

> **Business story first. Engineering evidence second.**

## Production Workflow

GitHub is the source of truth. Hugging Face is the deployment target.

```text
Change in GitHub
    ↓
Install CPU-only PyTorch + dependencies
    ↓
Run pytest
    ↓
Run retrieval benchmark
    ↓
Both pass
    ↓
Deploy main to Hugging Face
    ↓
Live human validation
```

The CI and Docker paths explicitly install CPU-only PyTorch because this agent does not require CUDA. This avoids unnecessarily large GPU dependency downloads and keeps the deployment path aligned with the actual runtime.

## Project Structure

```text
04-knowledge-retrieval-agent/
├── app.py
├── Dockerfile
├── requirements.txt
├── README.md
├── data/
│   └── sample_docs/
├── src/
│   ├── ingestion.py
│   ├── chunking.py
│   ├── retrieval.py
│   ├── answer_generation.py
│   ├── evaluation.py
│   └── demo_presentation.py
├── eval/
│   ├── test_questions.csv
│   └── run_eval.py
├── tests/
│   ├── test_retrieval.py
│   ├── test_presentation.py
│   └── test_app_smoke.py
└── .github/
    └── workflows/
        └── sync_to_huggingface.yml
```

## Public-Demo Safety

The repository uses only synthetic NimbusNote documents. Do not place private curriculum material, client data, financial records, legal records, medical information, credentials, or other sensitive documents in the public demo corpus.

## Reusable Primitive

Agent 4 contributes:

> **An approved-corpus hybrid-retrieval primitive that ranks evidence, exposes retrieval quality, and refuses to answer when the available evidence is insufficient.**

This primitive becomes a foundation for later systems that need document access, provenance, verification, research, or evidence-grounded decision support.

## Portfolio Progression

- **Agent 4:** Find the most relevant approved evidence and decide whether it is strong enough to answer from.
- **Agent 5:** Convert documents into structured work products while preserving source provenance.
- **Agent 6:** Evaluate whether supplied evidence supports or contradicts a claim strongly enough to rely on it.

The separation is intentional: **retrieval finds evidence; provenance traces evidence; verification judges evidence alignment.**
