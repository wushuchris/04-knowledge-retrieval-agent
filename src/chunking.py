from typing import List, Dict


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
    """Split text into overlapping character-based chunks."""
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    chunks = []
    start = 0
    text = text.strip()

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap

    return chunks


def build_chunks(documents: List[Dict], chunk_size: int = 900, overlap: int = 150) -> List[Dict]:
    """Create chunk records with source metadata."""
    chunk_records = []

    for doc in documents:
        chunks = chunk_text(doc["text"], chunk_size=chunk_size, overlap=overlap)
        for idx, chunk in enumerate(chunks):
            chunk_records.append(
                {
                    "chunk_id": f"{doc['source']}::chunk-{idx + 1}",
                    "source": doc["source"],
                    "chunk_number": idx + 1,
                    "text": chunk,
                }
            )

    return chunk_records
