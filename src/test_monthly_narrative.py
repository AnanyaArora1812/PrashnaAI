"""
test_monthly_narrative.py

Manual smoke test for the monthly transit narrative pipeline - full 12-month
run, timed, so we know what to expect before wiring this into app.py.
"""

import time

from astro.chart_calculator import calculate_birth_chart
from astro.transit_calculator import calculate_monthly_transits
from astro.monthly_narrative import generate_monthly_narrative_groq, get_groq_client
from rag.retriever import Retriever

FAISS_INDEX_PATH = "../datasets/processed/faiss_index/index.faiss"
FAISS_METADATA_PATH = "../datasets/processed/faiss_index/metadata.json"
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

chart = calculate_birth_chart(
    name="Test User",
    birth_date="1990-08-15",
    birth_time="14:30",
    utc_offset_hours=5.5,
    latitude=28.6139,
    longitude=77.2090,
    place_name="New Delhi, India",
)

monthly_transits = calculate_monthly_transits(chart, months=12)

retriever = Retriever(
    index_path=FAISS_INDEX_PATH,
    metadata_path=FAISS_METADATA_PATH,
    embedding_model_name=EMBEDDING_MODEL_NAME,
)
client = get_groq_client()

start = time.time()
results = []
for i, transit in enumerate(monthly_transits, start=1):
    month_start = time.time()
    result = generate_monthly_narrative_groq(chart, transit, retriever, client=client)
    month_elapsed = time.time() - month_start
    results.append(result)
    print(f"[{i}/12] {result['month_label']} done in {month_elapsed:.1f}s")

total_elapsed = time.time() - start
print(f"\nTOTAL TIME for 12 months: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")
print(f"Average per month: {total_elapsed/12:.1f}s")