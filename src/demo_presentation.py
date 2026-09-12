APP_CSS = """
<style>
    .main .block-container {
        max-width: 1080px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    .hero-card {
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 18px;
        padding: 1.5rem 1.6rem;
        margin-bottom: 1.1rem;
        background: rgba(128, 128, 128, 0.055);
    }
    .hero-kicker {
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        opacity: 0.72;
        margin-bottom: 0.55rem;
    }
    .hero-title {
        font-size: 2.15rem;
        font-weight: 760;
        line-height: 1.12;
        margin-bottom: 0.65rem;
    }
    .hero-copy {
        font-size: 1.08rem;
        line-height: 1.6;
        opacity: 0.88;
    }
    .principle-card {
        border-left: 4px solid #5b7cfa;
        padding: 0.85rem 1rem;
        margin: 0.8rem 0 1.4rem 0;
        background: rgba(91, 124, 250, 0.08);
        border-radius: 0 12px 12px 0;
    }
    .source-card {
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        margin-bottom: 0.65rem;
    }
    .source-name {
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .workflow-step {
        border: 1px solid rgba(128, 128, 128, 0.18);
        border-radius: 12px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.55rem;
    }
    .workflow-step strong {
        font-size: 1.02rem;
    }
    .boundary-card {
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        margin: 0.8rem 0;
        background: rgba(128, 128, 128, 0.035);
    }
</style>
"""


HERO_HTML = """
<div class="hero-card">
  <div class="hero-kicker">Agent 4 · Source-Cited Knowledge Retrieval</div>
  <div class="hero-title">How do you make AI answer from approved knowledge instead of from memory?</div>
  <div class="hero-copy">
    A fictional NimbusNote support team needs fast answers from internal policy, support, and security documents.
    This agent searches only the approved corpus, combines semantic and keyword retrieval, checks whether the match is strong enough,
    and either produces a source-cited evidence answer or abstains.
  </div>
</div>
<div class="principle-card">
  <strong>Operating rule:</strong> Retrieve first. Answer second. Cite always. Abstain when evidence is weak.
</div>
"""


CORPUS_HTML = """
<div class="source-card">
  <div class="source-name">📘 Product Policy Handbook</div>
  Refunds, account deletion, document retention, and product-policy guidance.
</div>
<div class="source-card">
  <div class="source-name">🎧 Customer Support Playbook</div>
  Password resets, enterprise onboarding, support escalation, and service procedures.
</div>
<div class="source-card">
  <div class="source-name">🔐 Security FAQ</div>
  SSO, access controls, encryption, audit logs, and sharing permissions.
</div>
"""


WORKFLOW_HTML = """
<div class="workflow-step"><strong>1 · Question enters</strong><br/>The user asks a question about the approved NimbusNote knowledge base.</div>
<div class="workflow-step"><strong>2 · Two retrieval signals score the corpus</strong><br/>Embeddings capture semantic similarity while BM25 captures keyword relevance.</div>
<div class="workflow-step"><strong>3 · Application code ranks and checks the evidence</strong><br/>The two signals are combined into a hybrid ranking, then the strongest match is checked against an explicit sufficiency threshold.</div>
<div class="workflow-step"><strong>4 · Answer from evidence—or abstain</strong><br/>Strong enough evidence becomes a source-cited extractive answer. Weak retrieval produces an explicit insufficient-evidence outcome.</div>
"""


BOUNDARY_HTML = """
<div class="boundary-card">
  <strong>What this agent can establish:</strong> which approved corpus chunks are most relevant to the question and what those chunks say.<br/><br/>
  <strong>What this agent does not establish:</strong> whether the underlying documents are factually correct in the outside world.
  Agent 6 later adds claim-vs-evidence verification; this project is specifically about retrieval quality and source grounding.
</div>
"""


DEFAULT_QUESTION = (
    "An enterprise customer asks whether NimbusNote supports SSO and what audit activity admins can review. "
    "What does the approved knowledge base say?"
)
