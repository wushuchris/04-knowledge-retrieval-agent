from pathlib import Path
from typing import List, Dict

SUPPORTED_EXTENSIONS = {".md", ".txt"}


def load_documents(data_dir: str | Path) -> List[Dict]:
    """Load markdown and text files from a directory."""
    data_path = Path(data_dir)
    documents = []

    if not data_path.exists():
        return documents

    for path in sorted(data_path.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            text = path.read_text(encoding="utf-8", errors="ignore").strip()
            if text:
                documents.append(
                    {
                        "source": path.name,
                        "path": str(path),
                        "text": text,
                    }
                )

    return documents
