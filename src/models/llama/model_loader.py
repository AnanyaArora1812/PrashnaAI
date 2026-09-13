"""
model_loader.py

Phase 8 of PrashnaAI RAG pipeline: loads the local quantized LLaMA
model (GGUF format) via llama-cpp-python for CPU inference.

Kept isolated so generate.py and ask.py don't need to know loading
details, and so the model can be swapped/reconfigured in one place.
"""

from __future__ import annotations

import logging
from pathlib import Path

from llama_cpp import Llama

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

_model_cache: dict[str, Llama] = {}


def get_llama_model(
    model_path: str | Path,
    n_ctx: int = 4096,
    n_threads: int | None = None,
) -> Llama:
    """
    Load (and cache) a local GGUF LLaMA model.

    Args:
        model_path: Path to the .gguf model file.
        n_ctx: Context window size (max tokens model can consider at once).
        n_threads: CPU threads to use. None lets llama.cpp auto-detect,
                   which is usually fine on limited-core machines like an i3.

    Returns:
        A loaded Llama instance, ready for text generation.
    """
    path_str = str(model_path)

    if path_str not in _model_cache:
        logger.info("Loading LLaMA model from: %s", path_str)
        logger.info("This may take 10-30 seconds on CPU...")

        _model_cache[path_str] = Llama(
            model_path=path_str,
            n_ctx=n_ctx,
            n_threads=n_threads,
            verbose=False,
        )
        logger.info("LLaMA model loaded successfully.")

    return _model_cache[path_str]