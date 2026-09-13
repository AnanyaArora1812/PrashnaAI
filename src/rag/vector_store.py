"""
vector_store.py

Phase 4 of PrashnaAI RAG pipeline: builds and persists a FAISS index
from chunk embeddings, plus a parallel metadata store so we can map
FAISS result indices back to actual chunk text/source/page.

Design:
- FAISS index stores ONLY vectors (it has no concept of text/metadata).
- We keep a separate metadata list, saved as JSON, where position i
  corresponds to FAISS vector i. This is the standard pattern for
  using FAISS with associated metadata.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import faiss
import numpy as np

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def build_faiss_index(embeddings: list[list[float]]) -> faiss.Index:
    """
    Build a FAISS index from a list of embedding vectors.

    Uses IndexFlatIP (inner product) on L2-normalized vectors, which
    is equivalent to cosine similarity search -- a standard, reliable
    choice for sentence-transformer embeddings.
    """
    vectors = np.array(embeddings, dtype="float32")
    faiss.normalize_L2(vectors)  # normalize so inner product = cosine similarity

    dimension = vectors.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(vectors)

    logger.info("Built FAISS index with %d vectors, dimension %d", index.ntotal, dimension)
    return index


def save_index(index: faiss.Index, metadata: list[dict], index_path: Path, metadata_path: Path) -> None:
    """Save the FAISS index and its associated metadata to disk."""
    index_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(index_path))
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    logger.info("Saved FAISS index to %s", index_path)
    logger.info("Saved metadata to %s", metadata_path)


def load_index(index_path: Path, metadata_path: Path) -> tuple[faiss.Index, list[dict]]:
    """Load a previously saved FAISS index and its metadata."""
    index = faiss.read_index(str(index_path))
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    return index, metadata