"""
test_retriever.py

Manual test for Phase 5: ask a question from the command line and see
what chunks get retrieved, with their page citations and similarity
scores. This is our first real end-to-end check that retrieval works
before we connect it to an LLM (Phase 6+).
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

from retriever import Retriever

CONFIG_PATH = Path("configs/config.yaml")
INDEX_PATH = Path("datasets/processed/faiss_index/index.faiss")
METADATA_PATH = Path("datasets/processed/faiss_index/metadata.json")


def main() -> None:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    retriever = Retriever(
        index_path=INDEX_PATH,
        metadata_path=METADATA_PATH,
        embedding_model_name=config["embedding_model"],
    )

    top_k = config.get("top_k", 5)

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Enter your question: ")

    results = retriever.retrieve(query, top_k=top_k)

    print(f"\nQuery: {query}\n")
    print(f"Top {len(results)} results:\n")
    for i, r in enumerate(results, start=1):
        print(f"--- Result {i} (score: {r['score']:.3f}) ---")
        print(f"Source: {r['source_file']}, Page: {r['page_number']}")
        print(r["text"][:400])
        print()


if __name__ == "__main__":
    main()
    