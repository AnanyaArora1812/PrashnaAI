"""
test_narrative.py

Quick manual test script - NOT part of the permanent pipeline, just for
checking that chart_calculator + Retriever + LLaMA generation all wire
together correctly through narrative.py.

Run from the project root:
    python src\\test_narrative.py

IMPORTANT: Double-check the four paths/names below against your actual
configs/config.yaml before running - if your FAISS index, metadata file,
embedding model name, or GGUF model path differ from what's written here,
update them to match your real config.
"""

from pathlib import Path

from rag.retriever import Retriever
from models.llama.model_loader import get_llama_model
from astro.chart_calculator import calculate_birth_chart
from astro.narrative import generate_topic_narrative

# ---------------------------------------------------------------------------
# 1. Build a sample birth chart (real calculation, no AI involved here)
# ---------------------------------------------------------------------------
chart = calculate_birth_chart(
    name="Test User",
    birth_date="1990-08-15",
    birth_time="14:30",
    utc_offset_hours=5.5,
    latitude=28.6139,
    longitude=77.2090,
    place_name="New Delhi, India",
)

print("Chart calculated. Ascendant:", chart.ascendant_sign)
print("Moon sign:", chart.moon_sign(), "| Moon nakshatra:", chart.moon_nakshatra())

# ---------------------------------------------------------------------------
# 2. Load your existing RAG retriever - CHECK these paths match config.yaml
# ---------------------------------------------------------------------------
retriever = Retriever(
    index_path=Path("datasets/processed/faiss_index/index.faiss"),
    metadata_path=Path("datasets/processed/faiss_index/metadata.json"),
    embedding_model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)

# ---------------------------------------------------------------------------
# 3. Load your existing LLaMA model - CHECK this path matches config.yaml
# ---------------------------------------------------------------------------
model = get_llama_model("models/llama_gguf/Llama-3.2-1B-Instruct-Q4_K_M.gguf")

# ---------------------------------------------------------------------------
# 4. Run one topic through the full pipeline: chart -> retrieval -> LLaMA
# ---------------------------------------------------------------------------
print("\nGenerating career narrative (this may take 30-90 seconds on CPU)...\n")

result = generate_topic_narrative(chart, "career", retriever, model)

print("=" * 70)
print("RETRIEVAL QUERY USED:")
print(result["retrieval_query"])
print("\nCHART FACTS HANDED TO THE LLM:")
print(result["chart_facts"])
print("\nNUMBER OF CHUNKS RETRIEVED:", len(result["retrieved_chunks"]))
print("\nGENERATED NARRATIVE:")
print(result["narrative"])
print("=" * 70)