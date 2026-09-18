from pathlib import Path

from rag.retriever import Retriever
from astro.chart_calculator import calculate_birth_chart
from astro.narrative_groq import generate_topic_narrative_groq

# same test person used in test_narrative.py and test_narrative_openai.py -
# keeping this identical across all three lets us compare local vs OpenAI
# vs Groq output side by side for the exact same chart.
chart = calculate_birth_chart(
    name="Test User",
    birth_date="1990-08-15",
    birth_time="14:30",
    utc_offset_hours=5.5,
    latitude=28.6139,
    longitude=77.2090,
    place_name="New Delhi, India",
)

# same FAISS index either way - only the generation backend changes.
retriever = Retriever(
    index_path=Path("datasets/processed/faiss_index/index.faiss"),
    metadata_path=Path("datasets/processed/faiss_index/metadata.json"),
    embedding_model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)

# needs GROQ_API_KEY set as an environment variable before running this,
# same reasoning as the OpenAI version - never hardcode it in a file.
result = generate_topic_narrative_groq(chart, "career", retriever)

print("\n--- CHART FACTS SENT TO THE MODEL ---")
print(result["chart_facts"])

print("\n--- GENERATED NARRATIVE (via", result["backend"], ") ---")
print(result["narrative"])