"""
retriever.py

Phase 5 of PrashnaAI RAG pipeline: given a natural-language question,
embeds it and searches the FAISS index for the most relevant chunks.

This is the core "R" in RAG -- Retrieval.
"""

from __future__ import annotations

import logging
from pathlib import Path

import faiss
import numpy as np

from rag.embeddings import get_embedding_model
from rag.vector_store import load_index

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class Retriever:
    """
    Wraps a FAISS index + metadata + embedding model to answer
    "what are the top-k most relevant chunks for this query?"
    """

    def __init__(self, index_path: Path, metadata_path: Path, embedding_model_name: str):
        logger.info("Loading FAISS index and metadata...")
        self.index, self.metadata = load_index(index_path, metadata_path)
        self.embedding_model_name = embedding_model_name
        logger.info("Retriever ready. Index has %d vectors.", self.index.ntotal)

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Retrieve the top_k most relevant chunks for a query.

        Args:
            query: Natural-language question.
            top_k: Number of chunks to return.

        Returns:
            List of dicts, each containing chunk text, source_file,
            page_number, and a similarity score, ordered by relevance
            (highest score first).
        """
        model = get_embedding_model(self.embedding_model_name)
        query_vector = model.encode([query], convert_to_numpy=True)
        query_vector = np.array(query_vector, dtype="float32")
        faiss.normalize_L2(query_vector)

        scores, indices = self.index.search(query_vector, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # FAISS returns -1 if fewer than top_k results exist
                continue
            chunk_meta = self.metadata[idx]
            results.append(
                {
                    "text": chunk_meta["text"],
                    "source_file": chunk_meta["source_file"],
                    "page_number": chunk_meta["page_number"],
                    "chunk_id": chunk_meta["chunk_id"],
                    "score": float(score),
                }
            )

        return results