from pathlib import Path

from src.demo_presentation import APP_CSS, BOUNDARY_HTML, DEFAULT_QUESTION, HERO_HTML


def test_business_presentation_is_centered_at_1080px():
    assert "max-width: 1080px" in APP_CSS


def test_hero_explains_approved_knowledge_boundary():
    assert "approved knowledge" in HERO_HTML.lower()
    assert "answer or abstains" in HERO_HTML.lower()
    assert "Retrieve first. Answer second. Cite always." in HERO_HTML


def test_boundary_separates_retrieval_from_truth_verification():
    assert "does not establish" in BOUNDARY_HTML
    assert "factually correct" in BOUNDARY_HTML
    assert "Agent 6" in BOUNDARY_HTML


def test_default_question_uses_enterprise_security_story():
    assert "enterprise customer" in DEFAULT_QUESTION.lower()
    assert "SSO" in DEFAULT_QUESTION
    assert "audit" in DEFAULT_QUESTION.lower()


def test_live_app_uses_real_observable_retrieval_path():
    app_source = Path("app.py").read_text(encoding="utf-8")

    assert "retriever.search_iter" in app_source
    assert "Searching the approved corpus" in app_source
    assert "Retrieved Evidence" in app_source
    assert "Retrieval Diagnostics" in app_source
