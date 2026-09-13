"""
text_cleaner.py

Phase 2a of PrashnaAI RAG pipeline: cleans raw OCR text.

Responsibilities:
- Normalize whitespace (collapse multiple spaces/newlines)
- Remove common OCR noise artifacts
- Preserve actual Devanagari/English content untouched

This does NOT chunk text -- that happens in chunker.py.
"""

from __future__ import annotations

import re


def clean_text(raw_text: str) -> str:
    """
    Clean a single page's raw OCR text.

    Args:
        raw_text: Unprocessed text as extracted by OCR (one line per
                   detected text region, joined with newlines).

    Returns:
        Cleaned text with normalized whitespace, ready for chunking.
    """
    if not raw_text:
        return ""

    text = raw_text

    # Collapse multiple consecutive newlines into a single space.
    # OCR output has one line per detected text region; for chunking
    # purposes we want continuous prose, not fragmented lines.
    text = re.sub(r"\n+", " ", text)

    # Collapse multiple spaces/tabs into one
    text = re.sub(r"[ \t]+", " ", text)

    # Remove stray isolated punctuation-only "noise" tokens that OCR
    # sometimes emits from page borders/scan artifacts (e.g. lone
    # symbols surrounded by spaces).
    text = re.sub(r"\s[|~`^*_=+<>]{1,3}\s", " ", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text