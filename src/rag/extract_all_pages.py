"""
extract_all_pages.py

Full OCR extraction run for the entire PDF (Phase 1b, production run).

Key design decisions:
- CHECKPOINTED: each page's result is written to disk immediately after
  OCR completes, not held in memory until the end. If this process is
  killed, closed, or crashes at page 400, pages 1-399 are already safe.
- RESUMABLE: on startup, it reads the existing output file and skips
  any page_number already present, so re-running this script continues
  where it left off instead of starting over.
- Output format: JSONL (one JSON object per line) at
  datasets/interim/ocr_pages.jsonl -- easy to append to, easy to resume,
  easy to stream-read later without loading all 800 pages into memory.
- SPEED TUNING (added for CPU-only i3 hardware):
  - render_page_to_array caps the longest side at max_dimension pixels
    instead of a fixed zoom multiplier, so pages with very high original
    scan resolution don't balloon into huge, slow images.
  - readtext uses a smaller canvas_size and batch_size to reduce
    per-page detection/recognition cost on limited CPU cores.
"""

from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

import pymupdf
import easyocr
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs_ocr_extraction.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

PDF_PATH = Path("datasets/raw/pdfs") / "BPHS पराशरहोराशास्त्र Brihat Parashar Hora Shastra.pdf"
OUTPUT_PATH = Path("datasets/interim/ocr_pages.jsonl")
LANGUAGES = ["hi", "en"]
MAX_DIMENSION = 1000  # longest side of rendered page image, in pixels

def load_completed_pages(output_path: Path) -> set[int]:
    """Read already-processed page numbers from the output file, if it exists."""
    if not output_path.exists():
        return set()

    completed = set()
    with open(output_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                completed.add(record["page_number"])
            except (json.JSONDecodeError, KeyError):
                continue
    return completed


def render_page_to_array(doc: pymupdf.Document, page_number: int, max_dimension: int = MAX_DIMENSION):
    """
    Render a 1-indexed page to a numpy image array, capping the longest
    side at max_dimension pixels. This normalizes processing time across
    pages regardless of the original scan's resolution (some pages in
    this PDF are much higher-res than others, causing wildly inconsistent
    OCR times with a fixed zoom multiplier).
    """
    page = doc[page_number - 1]
    rect = page.rect
    longest_side = max(rect.width, rect.height)
    zoom = max_dimension / longest_side

    matrix = pymupdf.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=matrix)
    img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
        pix.height, pix.width, pix.n
    )
    if pix.n == 4:
        img_array = img_array[:, :, :3]
    return img_array


def main() -> None:
    if not PDF_PATH.exists():
        logger.error("PDF not found at: %s", PDF_PATH)
        sys.exit(1)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    completed = load_completed_pages(OUTPUT_PATH)
    logger.info("Found %d already-completed pages. Will skip these.", len(completed))

    doc = pymupdf.open(str(PDF_PATH))
    total_pages = len(doc)
    logger.info("PDF has %d total pages.", total_pages)

    logger.info("Initializing EasyOCR reader (languages: %s)...", LANGUAGES)
    reader = easyocr.Reader(LANGUAGES, gpu=False)

    remaining = [p for p in range(1, total_pages + 1) if p not in completed]
    logger.info("Pages remaining to process: %d", len(remaining))

    start_time = time.time()

    # Open output file in append mode so we never overwrite prior progress
    with open(OUTPUT_PATH, "a", encoding="utf-8") as out_f:
        for idx, page_num in enumerate(remaining, start=1):
            page_start = time.time()
            try:
                img_array = render_page_to_array(doc, page_num)
                ocr_result = reader.readtext(
                    img_array, detail=1, canvas_size=1000, batch_size=2
                )

                texts = [item[1] for item in ocr_result]
                confidences = [item[2] for item in ocr_result]
                page_text = "\n".join(texts)
                avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

                record = {
                    "source_file": PDF_PATH.name,
                    "page_number": page_num,
                    "text": page_text,
                    "confidence": round(avg_conf, 3),
                }
            except Exception as exc:
                logger.error("Page %d failed: %s", page_num, exc)
                record = {
                    "source_file": PDF_PATH.name,
                    "page_number": page_num,
                    "text": "",
                    "confidence": 0.0,
                    "error": str(exc),
                }

            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            out_f.flush()  # ensure it's actually on disk, not buffered in memory

            page_elapsed = time.time() - page_start
            overall_elapsed = time.time() - start_time
            avg_per_page = overall_elapsed / idx
            eta_seconds = avg_per_page * (len(remaining) - idx)

            logger.info(
                "[%d/%d] Page %d done in %.1fs (conf %.2f). ETA: %.0f min remaining.",
                idx,
                len(remaining),
                page_num,
                page_elapsed,
                record["confidence"],
                eta_seconds / 60,
            )

    doc.close()
    logger.info("EXTRACTION COMPLETE. Output saved to: %s", OUTPUT_PATH)


if __name__ == "__main__":
    main() 