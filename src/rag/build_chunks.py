"""
build_chunks.py

Runs Phase 2 end-to-end: reads raw OCR pages, cleans them, chunks them,
and saves the result to datasets/processed/chunks/chunks.jsonl.

This is a fast, one-time (or re-runnable) batch job -- no OCR/model
inference involved, so it should complete in seconds.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import yaml

from text_cleaner import clean_text
from chunker import chunk_page_text

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

OCR_INPUT_PATH = Path("datasets/interim/ocr_pages.jsonl")
CHUNKS_OUTPUT_PATH = Path("datasets/processed/chunks/chunks.jsonl")
CONFIG_PATH = Path("configs/config.yaml")


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    if not OCR_INPUT_PATH.exists():
        logger.error("OCR input not found at: %s", OCR_INPUT_PATH)
        return

    config = load_config()
    chunk_size = config["chunk_size"]
    chunk_overlap = config["chunk_overlap"]
    logger.info("Using chunk_size=%d, chunk_overlap=%d", chunk_size, chunk_overlap)

    CHUNKS_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    total_pages = 0
    total_chunks = 0
    empty_after_clean = 0

    with open(OCR_INPUT_PATH, "r", encoding="utf-8") as in_f, \
         open(CHUNKS_OUTPUT_PATH, "w", encoding="utf-8") as out_f:

        for line in in_f:
            line = line.strip()
            if not line:
                continue

            record = json.loads(line)
            total_pages += 1

            cleaned = clean_text(record["text"])
            if not cleaned:
                empty_after_clean += 1
                continue

            page_chunks = chunk_page_text(
                text=cleaned,
                source_file=record["source_file"],
                page_number=record["page_number"],
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )

            min_len = config.get("min_chunk_length", 0)
            for chunk in page_chunks:
                if len(chunk.text.strip()) < min_len:
                    continue
                out_f.write(
                    json.dumps(
                        {
                            "chunk_id": chunk.chunk_id,
                            "source_file": chunk.source_file,
                            "page_number": chunk.page_number,
                            "text": chunk.text,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                total_chunks += 1

    logger.info("Processed %d pages -> %d chunks", total_pages, total_chunks)
    logger.info("Pages that became empty after cleaning: %d", empty_after_clean)
    logger.info("Saved to: %s", CHUNKS_OUTPUT_PATH)


if __name__ == "__main__":
    main()