"""Bootstrap script for ingesting knowledge sources into the vector store."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from shared import get_settings


def discover_documents(source_directory: Path) -> Iterable[Path]:
    """Yield documents from the given directory that should be ingested."""

    for path in source_directory.glob("**/*"):
        if path.is_file() and path.suffix.lower() in {".md", ".txt", ".pdf"}:
            yield path


def main() -> None:
    """Demonstrate how ingestion jobs resolve shared configuration."""

    settings = get_settings()
    vector_store_path = Path(settings.vector_store_path)
    vector_store_path.mkdir(parents=True, exist_ok=True)

    print("Using Ollama host:", settings.ollama_host)
    print("Target model:", settings.ollama_model)
    print("Vector store path:", vector_store_path.resolve())
    # A real implementation would chunk documents and persist embeddings here.


if __name__ == "__main__":
    main()
