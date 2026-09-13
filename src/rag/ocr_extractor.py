"""
ocr_extractor.py

Phase 1b of PrashnaAI RAG pipeline: OCR-based text extraction for
scanned/image-only PDFs.

Used when pdf_loader.py's direct text extraction returns empty pages
(i.e., the PDF has no real text layer, only page images).

Pipeline for each page:
    PDF page -> rendered as image (PyMuPDF) -> OCR (EasyOCR) -> text

This module is intentionally separate from pdf_loader.py so that:
- Normal (non-scanned) PDFs never pay the OCR cost.
- OCR logic, which is slower and has different dependencies, stays isolated.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pymupdf  # modern import name (replaces `import fitz`)
import easyocr

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


@dataclass
class OCRPageRecord:
    """Represents a single OCR'd page of text with metadata."""

    source_file: str
    page_number: int  # 1-indexed
    text: str
    confidence: float  # average OCR confidence for this page (0-1)


class OCRExtractionError(Exception):
    """Raised when OCR extraction fails for a PDF."""


def _get_reader(languages: list[str]) -> easyocr.Reader:
    """
    Create an EasyOCR reader for the given languages.

    Note: EasyOCR downloads model weights automatically on first use
    for each language (one-time, requires internet, ~100MB+).
    Subsequent runs use the cached models.
    """
    logger.info("Initializing EasyOCR reader for languages: %s", languages)
    # gpu=False because CUDA is not available on this machine (see project config)
    return easyocr.Reader(languages, gpu=False)


def render_page_to_image(
    pdf_path: str | Path, page_number: int, zoom: float = 2.0
):
    """
    Render a single PDF page (1-indexed) to a PIL-compatible image array.

    Args:
        pdf_path: Path to the PDF.
        page_number: 1-indexed page number to render.
        zoom: Scale factor for rendering resolution. Higher = sharper
              image = better OCR accuracy, but slower. 2.0 is a
              reasonable default (roughly 144 DPI equivalent).

    Returns:
        A numpy array (H, W, 3) representing the rendered page image.
    """
    doc = pymupdf.open(str(pdf_path))
    try:
        if page_number < 1 or page_number > len(doc):
            raise OCRExtractionError(
                f"Page {page_number} out of range (PDF has {len(doc)} pages)"
            )
        page = doc[page_number - 1]  # pymupdf is 0-indexed internally
        matrix = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=matrix)
        # Convert pixmap -> numpy array (H, W, 3) for EasyOCR
        import numpy as np

        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width, pix.n
        )
        if pix.n == 4:  # RGBA -> RGB
            img_array = img_array[:, :, :3]
        return img_array
    finally:
        doc.close()


def ocr_pages(
    pdf_path: str | Path,
    page_numbers: list[int],
    languages: list[str] | None = None,
    zoom: float = 2.0,
) -> list[OCRPageRecord]:
    """
    Run OCR on specific pages of a PDF.

    Args:
        pdf_path: Path to the PDF.
        page_numbers: 1-indexed page numbers to OCR.
        languages: EasyOCR language codes. Defaults to ['hi', 'en']
                   (Hindi covers Devanagari script; English catches any
                   Latin-script headers/page numbers/English commentary).
        zoom: Rendering resolution multiplier (see render_page_to_image).

    Returns:
        List of OCRPageRecord, one per requested page, in the order given.
    """
    if languages is None:
        languages = ["hi", "en"]

    path = Path(pdf_path)
    if not path.exists():
        raise OCRExtractionError(f"PDF not found at: {path}")

    reader = _get_reader(languages)
    results: list[OCRPageRecord] = []

    for page_num in page_numbers:
        logger.info("OCR processing page %d...", page_num)
        try:
            img_array = render_page_to_image(path, page_num, zoom=zoom)
            ocr_result = reader.readtext(img_array, detail=1)

            # ocr_result is a list of (bbox, text, confidence) tuples
            texts = [item[1] for item in ocr_result]
            confidences = [item[2] for item in ocr_result]

            page_text = "\n".join(texts)
            avg_confidence = (
                sum(confidences) / len(confidences) if confidences else 0.0
            )

            results.append(
                OCRPageRecord(
                    source_file=path.name,
                    page_number=page_num,
                    text=page_text,
                    confidence=avg_confidence,
                )
            )
            logger.info(
                "Page %d done. %d text regions found, avg confidence %.2f",
                page_num,
                len(texts),
                avg_confidence,
            )
        except Exception as exc:
            logger.error("OCR failed on page %d: %s", page_num, exc)
            results.append(
                OCRPageRecord(
                    source_file=path.name,
                    page_number=page_num,
                    text="",
                    confidence=0.0,
                )
            )

    return results


if __name__ == "__main__":
    # Sample test: OCR just the first 5 pages to check quality/speed
    # before committing to the full 800-page book.
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ocr_extractor.py <filename.pdf> [num_pages]")
        sys.exit(1)

    pdf_dir = Path("datasets/raw/pdfs")
    target = pdf_dir / sys.argv[1]
    num_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    sample_pages = list(range(1, num_pages + 1))
    records = ocr_pages(target, sample_pages)

    for rec in records:
        print(f"\n{'=' * 50}")
        print(f"Page {rec.page_number} (confidence: {rec.confidence:.2f})")
        print("=" * 50)
        print(rec.text[:800] if rec.text else "(no text detected)")