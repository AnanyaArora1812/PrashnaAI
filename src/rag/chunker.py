"""
chunker.py

Phase 2b of PrashnaAI RAG pipeline: splits cleaned page text into
overlapping chunks suitable for embedding.

Chunking strategy (v1, kept intentionally simple):
- Chunk per page, preserving accurate page-level citation metadata.
- If a page's cleaned text exceeds chunk_size, split it into multiple
  overlapping chunks within that page.
- If a page's text is shorter than chunk_size, it becomes a single chunk.

This keeps "Source: X, Page: Y" citations accurate to a single page,
per the project's RAG requirements (Section 12).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Chunk:
    """A single chunk of text with source metadata."""

    chunk_id: str
    source_file: str
    page_number: int
    text: str


def chunk_page_text(
    text: str,
    source_file: str,
    page_number: int,
    chunk_size: int = 800,
    chunk_overlap: int = 150,
) -> list[Chunk]:
    """
    Split a single page's cleaned text into overlapping chunks.

    Args:
        text: Cleaned page text (output of text_cleaner.clean_text).
        source_file: Original PDF filename, for citation metadata.
        page_number: 1-indexed page number, for citation metadata.
        chunk_size: Target max characters per chunk.
        chunk_overlap: Characters of overlap between consecutive chunks,
                       so context isn't lost at chunk boundaries.

    Returns:
        List of Chunk objects. Empty list if text is empty.
    """
    if not text:
        return []

    if len(text) <= chunk_size:
        return [
            Chunk(
                chunk_id=f"p{page_number}_c0",
                source_file=source_file,
                page_number=page_number,
                text=text,
            )
        ]

    chunks: list[Chunk] = []
    start = 0
    chunk_index = 0

    while start < len(text):
        end = start + chunk_size
        chunk_text_value = text[start:end]

        chunks.append(
            Chunk(
                chunk_id=f"p{page_number}_c{chunk_index}",
                source_file=source_file,
                page_number=page_number,
                text=chunk_text_value,
            )
        )

        chunk_index += 1
        # Move start forward by (chunk_size - overlap) so consecutive
        # chunks share `overlap` characters of context
        start += chunk_size - chunk_overlap

    return chunks