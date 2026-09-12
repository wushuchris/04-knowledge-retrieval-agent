from typing import Dict, List
import re

from src.retrieval import assess_evidence


def clean_markdown(text: str) -> str:
    text = text.replace("\n", " ")
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"#+\s*", "", text)
    text = re.sub(r"[-*+]\s+", "", text)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def question_terms(question: str) -> List[str]:
    cleaned = re.sub(r"[^a-zA-Z0-9 ]", " ", question.lower())
    tokens = [token for token in cleaned.split() if len(token) > 2]
    stop_words = {
        "what", "when", "where", "which", "who", "why", "how",
        "the", "and", "for", "that", "this", "from", "with", "about",
        "can", "use", "uses", "using", "are", "is", "of",
    }
    return [token for token in tokens if token not in stop_words]


def extract_sentences(text: str) -> List[str]:
    cleaned = clean_markdown(text)
    parts = re.split(r"(?<=[.!?])\s+", cleaned)
    sentences = [part.strip() for part in parts if len(part.strip()) > 20]
    return sentences


def score_sentence(sentence: str, terms: List[str]) -> float:
    lower = sentence.lower()
    term_matches = sum(1 for term in terms if term in lower)
    length_bonus = min(len(sentence.split()) / 25, 1)
    return term_matches * 2 + length_bonus


def extract_relevant_sentences(text: str, question: str, max_sentences: int = 2) -> List[str]:
    sentences = extract_sentences(text)
    if not sentences:
        return []

    terms = question_terms(question)
    scored = [(score_sentence(sentence, terms), sentence) for sentence in sentences]
    scored.sort(key=lambda pair: (pair[0], len(pair[1].split())), reverse=True)

    chosen = []
    for _, sentence in scored:
        if len(chosen) >= max_sentences:
            break
        if sentence not in chosen:
            chosen.append(sentence)

    return chosen or sentences[:max_sentences]


def estimate_confidence(results: List[Dict]) -> str:
    evidence = assess_evidence(results)
    if evidence["status"] == "sufficient":
        return "High enough to answer from the approved corpus"
    if evidence["status"] == "limited":
        return "Limited — answer should be qualified"
    return "Insufficient — abstain"


def build_evidence_answer(question: str, results: List[Dict]) -> str:
    evidence = assess_evidence(results)
    if evidence["status"] == "insufficient":
        return (
            "**Evidence status: Insufficient**\n\n"
            "I could not find a strong enough match in the approved document collection to answer this question reliably. "
            "I will not fill the gap from model memory or outside knowledge."
        )

    sorted_results = sorted(results, key=lambda item: item.get("hybrid_score", 0), reverse=True)
    top_results = sorted_results[:3]

    if evidence["status"] == "limited":
        lead = (
            "**Evidence status: Limited**\n\n"
            "The corpus contains potentially relevant material, but the retrieval match is weak. Treat this as a qualified evidence extract rather than a confident answer."
        )
    else:
        lead = "**Evidence status: Sufficient retrieval match**"

    answer_lines = [
        lead,
        "",
        "Based only on the retrieved evidence:",
        "",
    ]

    cited_sentences = 0
    for item in top_results:
        chunk_num = item.get("chunk_number", "?")
        source = item.get("source", "unknown source")
        sentences = extract_relevant_sentences(item.get("text", ""), question, max_sentences=1)
        for sentence in sentences:
            answer_lines.append(f"- {sentence} **[{source} · chunk {chunk_num}]**")
            cited_sentences += 1

    if cited_sentences == 0:
        answer_lines.append("- No concise answer sentence could be extracted from the retrieved chunks.")

    answer_lines.extend(["", "**Evidence used**", ""])
    for item in top_results:
        answer_lines.append(
            f"- {item.get('source', 'unknown source')} · chunk {item.get('chunk_number', '?')} · hybrid score {item.get('hybrid_score', 0):.3f}"
        )

    return "\n".join(answer_lines)
