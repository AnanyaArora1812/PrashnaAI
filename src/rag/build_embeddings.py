"""
build_embeddings.py

Runs Phase 3 end-to-end: reads chunks.jsonl, generates embeddings for
every chunk, and saves vectors + metadata to
datasets/processed/embeddings/embeddings.jsonl.

First run will download the embedding model (~470MB, one-time,
requires internet). Subsequent runs reuse the cached model.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import yaml

from embeddings import embed_texts

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CHUNKS_PATH = Path("datasets/processed/chunks/chunks.jsonl")
OUTPUT_PATH = Path("datasets/processed/embeddings/embeddings.jsonl")
CONFIG_PATH = Path("configs/config.yaml")


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    if not CHUNKS_PATH.exists():
        logger.error("Chunks file not found at: %s", CHUNKS_PATH)
        return

    config = load_config()
    model_name = config["embedding_model"]

    # Load all chunks into memory (2,155 small text records is trivial size)
    chunks = []
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))

    logger.info("Loaded %d chunks from %s", len(chunks), CHUNKS_PATH)

    texts = [c["text"] for c in chunks]
    vectors = embed_texts(texts, model_name=model_name)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as out_f:
        for chunk, vector in zip(chunks, vectors):
            record = {
                "chunk_id": chunk["chunk_id"],
                "source_file": chunk["source_file"],
                "page_number": chunk["page_number"],
                "text": chunk["text"],
                "embedding": vector,
            }
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")

    logger.info("Saved %d embeddings to %s", len(chunks), OUTPUT_PATH)


if __name__ == "__main__":
    main()

