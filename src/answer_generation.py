from typing import List, Dict
import re


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
    scored = [
        (score_sentence(sentence, terms), sentence)
        for sentence in sentences
    ]
    scored.sort(key=lambda pair: (pair[0], len(pair[1].split())), reverse=True)
    chosen = []
    for _, sentence in scored:
        if len(chosen) >= max_sentences:
            break
        if sentence not in chosen:
            chosen.append(sentence)

    if not chosen:
        return sentences[:max_sentences]
    return chosen


def estimate_confidence(results: List[Dict]) -> str:
    if not results:
        return "No evidence"

    top_score = max(result.get("hybrid_score", 0) for result in results)
    if top_score >= 0.60:
        return "High"
    if top_score >= 0.40:
        return "Medium"
    if top_score >= 0.25:
        return "Low"
    return "Very low"


def build_evidence_answer(question: str, results: List[Dict]) -> str:
    if not results:
        return "I could not find enough evidence in the document collection to answer that question."

    sorted_results = sorted(results, key=lambda item: item.get("hybrid_score", 0), reverse=True)
    top_results = sorted_results[:3]
    confidence = estimate_confidence(top_results)

    answer_lines = [
        f"Confidence: **{confidence}**",
        "",
        "Based on the top retrieved evidence, the most relevant sentences are:",
        "",
    ]

    for item in top_results:
        chunk_num = item.get("chunk_number", "?")
        source = item.get("source", "unknown source")
        sentences = extract_relevant_sentences(item.get("text", ""), question, max_sentences=1)
        if not sentences:
            continue

        for sentence in sentences:
            answer_lines.append(f"- {sentence} [{source} chunk {chunk_num}]")

    if len(answer_lines) <= 4:
        answer_lines.append("- No concise sentences could be extracted from the top results.")

    answer_lines.extend(["", "Sources used:", ""])
    for item in top_results:
        chunk_num = item.get("chunk_number", "?")
        source = item.get("source", "unknown source")
        hybrid_score = item.get("hybrid_score", 0)
        answer_lines.append(
            f"- {source}, chunk {chunk_num}, hybrid score {hybrid_score:.3f}"
        )

    return "\n".join(answer_lines)
