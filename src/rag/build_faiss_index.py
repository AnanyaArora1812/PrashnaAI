"""
build_faiss_index.py

Runs Phase 4 end-to-end: reads embeddings.jsonl, builds a FAISS index,
and saves it (plus metadata) to datasets/processed/faiss_index/.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from vector_store import build_faiss_index, save_index

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

EMBEDDINGS_PATH = Path("datasets/processed/embeddings/embeddings.jsonl")
INDEX_PATH = Path("datasets/processed/faiss_index/index.faiss")
METADATA_PATH = Path("datasets/processed/faiss_index/metadata.json")


def main() -> None:
    if not EMBEDDINGS_PATH.exists():
        logger.error("Embeddings file not found at: %s", EMBEDDINGS_PATH)
        return

    embeddings = []
    metadata = []

    with open(EMBEDDINGS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            embeddings.append(record["embedding"])
            metadata.append(
                {
                    "chunk_id": record["chunk_id"],
                    "source_file": record["source_file"],
                    "page_number": record["page_number"],
                    "text": record["text"],
                }
            )

    logger.info("Loaded %d embeddings", len(embeddings))

    index = build_faiss_index(embeddings)
    save_index(index, metadata, INDEX_PATH, METADATA_PATH)

    logger.info("Phase 4 complete. FAISS index ready for retrieval.")


if __name__ == "__main__":
    main()