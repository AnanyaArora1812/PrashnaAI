"""
ask.py

PrashnaAI CLI entry point: full RAG pipeline from question to grounded
answer with citations, usable without any frontend.

Usage:
    python src/ask.py "your question here"
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

# Allow imports from src/rag, src/models, src/inference as top-level packages
sys.path.insert(0, str(Path(__file__).parent))

from rag.retriever import Retriever
from inference.generate import generate_answer

CONFIG_PATH = Path("configs/config.yaml")
INDEX_PATH = Path("datasets/processed/faiss_index/index.faiss")
METADATA_PATH = Path("datasets/processed/faiss_index/metadata.json")
MODEL_PATH = Path("models/llama_gguf/Llama-3.2-1B-Instruct-Q4_K_M.gguf")


def main() -> None:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = input("Ask PrashnaAI a question: ")

    print("\nRetrieving relevant passages...")
    retriever = Retriever(
        index_path=INDEX_PATH,
        metadata_path=METADATA_PATH,
        embedding_model_name=config["embedding_model"],
    )
    chunks = retriever.retrieve(question, top_k=config.get("top_k", 5))

    print("Generating answer (this may take a moment on CPU)...\n")
    answer = generate_answer(
        question=question,
        retrieved_chunks=chunks,
        model_path=str(MODEL_PATH),
        max_new_tokens=config.get("max_new_tokens", 512),
        temperature=config.get("temperature", 0.3),
    )

    print("=" * 60)
    print(f"Question: {question}")
    print("=" * 60)
    print(f"\nAnswer:\n{answer}\n")
    print("-" * 60)
    print("Sources:")
    seen_pages = set()
    for chunk in chunks:
        key = (chunk["source_file"], chunk["page_number"])
        if key not in seen_pages:
            print(f"  - {chunk['source_file']}, Page {chunk['page_number']}")
            seen_pages.add(key)


if __name__ == "__main__":
    main()