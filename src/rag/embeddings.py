"""
embeddings.py

Phase 3 of PrashnaAI RAG pipeline: generates embedding vectors for
text chunks using a sentence-transformers model.

Responsibilities:
- Load the configured embedding model
- Encode a batch of chunk texts into vectors
- Keep this logic isolated so vector_store.py (Phase 4) and
  retriever.py (Phase 5) don't need to know embedding details.
"""

from __future__ import annotations

import logging

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

_model_cache: dict[str, SentenceTransformer] = {}


def get_embedding_model(model_name: str) -> SentenceTransformer:
    """
    Load (and cache) a sentence-transformers embedding model.

    Caching avoids reloading the model repeatedly within the same
    process if this function is called multiple times.
    """
    if model_name not in _model_cache:
        logger.info("Loading embedding model: %s (first load may download it)", model_name)
        _model_cache[model_name] = SentenceTransformer(model_name)
        logger.info("Embedding model loaded.")
    return _model_cache[model_name]


def embed_texts(texts: list[str], model_name: str, batch_size: int = 32) -> list[list[float]]:
    """
    Generate embedding vectors for a list of texts.

    Args:
        texts: List of chunk text strings.
        model_name: sentence-transformers model identifier.
        batch_size: How many texts to embed at once (memory/speed tradeoff).

    Returns:
        List of embedding vectors (as plain Python lists of floats),
        in the same order as the input texts.
    """
    model = get_embedding_model(model_name)
    logger.info("Embedding %d texts (batch_size=%d)...", len(texts), batch_size)
    vectors = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
    )
    logger.info("Embedding complete. Vector dimension: %d", vectors.shape[1])
    return vectors.tolist()