"""
pdf_loader.py

Phase 1 of PrashnaAI RAG pipeline: PDF ingestion and page-level text extraction.

Responsibilities:
- Load a PDF from disk
- Extract raw text page-by-page
- Attach metadata (source filename, page number) to each page
- Return a structured list of page records for downstream cleaning/chunking

This module does NOT clean or chunk text — that happens in text_cleaner.py
and chunker.py (Phase 2). Keeping this module focused on extraction only.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


@dataclass
class PageRecord:
    """Represents a single extracted page of text with metadata."""

    source_file: str
    page_number: int  # 1-indexed, matches how a human would reference the page
    text: str


class PDFLoadError(Exception):
    """Raised when a PDF cannot be found or read."""


def load_pdf_pages(pdf_path: str | Path) -> list[PageRecord]:
    """
    Extract text from a PDF, page by page, preserving page metadata.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        A list of PageRecord objects, one per page, in page order.
        Pages with no extractable text are still included (with empty
        string) so page numbering stays accurate downstream.

    Raises:
        PDFLoadError: If the file does not exist or cannot be parsed.
    """
    path = Path(pdf_path)

    if not path.exists():
        raise PDFLoadError(f"PDF not found at: {path}")

    if path.suffix.lower() != ".pdf":
        raise PDFLoadError(f"Expected a .pdf file, got: {path.suffix}")

    logger.info("Loading PDF: %s", path.name)

    try:
        reader = PdfReader(str(path))
    except Exception as exc:  # pypdf can raise various parsing errors
        raise PDFLoadError(f"Failed to open PDF '{path.name}': {exc}") from exc

    num_pages = len(reader.pages)
    logger.info("PDF has %d pages", num_pages)

    records: list[PageRecord] = []
    empty_page_count = 0

    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception as exc:
            logger.warning("Failed to extract text on page %d: %s", i, exc)
            text = ""

        if not text.strip():
            empty_page_count += 1

        records.append(
            PageRecord(source_file=path.name, page_number=i, text=text)
        )

    if empty_page_count:
        logger.warning(
            "%d of %d pages had no extractable text (likely scanned images "
            "or blank pages). OCR is not implemented yet.",
            empty_page_count,
            num_pages,
        )

    logger.info("Extraction complete for %s", path.name)
    return records


if __name__ == "__main__":
    # Quick manual test: point this at any PDF in datasets/raw/pdfs/
    import sys

    if len(sys.argv) < 2:
        print("Usage: python pdf_loader.py <filename.pdf>")
        print("Looking in datasets/raw/pdfs/ by default.")
        sys.exit(1)

    pdf_dir = Path("datasets/raw/pdfs")
    target = pdf_dir / sys.argv[1]

    pages = load_pdf_pages(target)
    print(f"\nExtracted {len(pages)} pages from {target.name}\n")
    print("--- Preview of page 1 ---")
    print(pages[0].text[:500] if pages else "(no pages)")
    