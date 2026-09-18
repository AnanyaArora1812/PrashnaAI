"""
narrative.py

Wires the deterministic chart output (chart_calculator.py) into the existing
RAG pipeline (rag/retriever.py) and LLaMA generation (models/llama/model_loader.py)
to produce grounded, readable predictions.

ARCHITECTURE NOTE (do not violate this):
The LLM NEVER invents chart facts. Every prompt sent to it already states the
real computed placements in plain language; the LLM's only job is to (a) find
relevant book passages via retrieval, and (b) turn [real chart facts + real
book text] into a readable paragraph. If retrieval finds nothing relevant for
a topic, the model is told to say so rather than to fill in gaps.

SCOPE: this first pass covers natal-chart topics only (career, finance,
family, relationships, personality) using the D1 Rashi chart. Monthly/yearly
predictions require a separate transit (Gochar) calculation - current
planetary positions compared against the birth chart - which is not yet
implemented; see `TODO: transits` below for where that would plug in.

Reuses your existing modules directly:
    from rag.retriever import Retriever
    from models.llama.model_loader import get_llama_model
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from astro.chart_calculator import BirthChart, RASHIS, RASHI_LORDS

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# ---------------------------------------------------------------------------
# Which houses govern which life-area topic (classical Parashari significations)
# ---------------------------------------------------------------------------

TOPIC_HOUSES = {
    "career": [10, 6],          # 10th = profession/status, 6th = daily work/service
    "finance": [2, 11],          # 2nd = accumulated wealth, 11th = income/gains
    "family": [4, 2],            # 4th = home/mother/domestic life, 2nd = family lineage
    "relationships": [7],        # 7th = marriage/partnerships
    "personality": [1],          # 1st = self/ascendant
}

TOPIC_LABELS = {
    "career": "career and professional life",
    "finance": "financial stability and wealth",
    "family": "family and domestic life",
    "relationships": "relationships and marriage",
    "personality": "core personality and nature",
}


NARRATIVE_PROMPT_TEMPLATE = """You are PrashnaAI, a Vedic astrology assistant. You are given REAL, precisely calculated birth chart placements for a person, plus REAL passages from a classical astrology text (Brihat Parashar Hora Shastra). Your job is to weave these into a warm, readable prediction.

Rules:
- Treat the "Real chart facts" section as ground truth. Copy sign names, house numbers, and nakshatra names EXACTLY as given below - never attach a nakshatra name to a house number, never swap which sign belongs to which house, and never state a placement not listed below.
- Use the "Reference passages" only if they are actually relevant to the chart facts given. If they are not relevant, rely on the chart facts alone and general classical principles, and do not pretend the passages support something they don't.
- If neither the chart facts nor the passages give enough basis for a confident statement, say the indications are mixed or unclear rather than guessing.
- Do NOT invent a specific number of years, ages, or dates (e.g. "next 12 years") - this reading is about lifelong natal tendencies, not a timed forecast. Avoid time-bound phrasing entirely.
- Write 4-6 sentences, warm and readable, like an experienced astrologer speaking to the person - not a bullet list, not a dry citation of rules.
- Do not mention "the text says" or cite sources by name; synthesize naturally.

Real chart facts ({topic_label}) - use these exact sign/house/nakshatra pairings, do not mix them up:
{chart_facts}

Reference passages from the classical text:
{context}

Write the prediction now, staying strictly consistent with the chart facts above:"""


@dataclass
class TopicRetrievalQuery:
    topic: str
    query_text: str
    chart_facts: str


def _house_sign_index(ascendant_sign_index: int, house_number: int) -> int:
    """Whole-sign: house N's sign is (house N-1) signs ahead of the ascendant."""
    return (ascendant_sign_index + house_number - 1) % 12


def _house_lord(ascendant_sign_index: int, house_number: int) -> str:
    sign_idx = _house_sign_index(ascendant_sign_index, house_number)
    return RASHI_LORDS[sign_idx]


def build_topic_query(chart: BirthChart, topic: str) -> TopicRetrievalQuery:
    """
    Given a computed BirthChart and a topic key (career/finance/family/
    relationships/personality), produce:
      - a natural-language retrieval query to search the book with
      - a plain-language statement of the real chart facts for that topic
    """
    if topic not in TOPIC_HOUSES:
        raise ValueError(f"Unknown topic '{topic}'. Valid: {list(TOPIC_HOUSES)}")

    houses = TOPIC_HOUSES[topic]
    fact_lines = [
        f"1. Ascendant (Lagna) sign = {chart.ascendant_sign}. (This is the 1st house sign.)",
    ]
    query_fragments = [f"{chart.ascendant_sign} lagna"]
    fact_num = 2

    for house_num in houses:
        sign_idx = _house_sign_index(chart.ascendant_sign_index, house_num)
        sign = RASHIS[sign_idx]
        lord = RASHI_LORDS[sign_idx]

        # which planets (if any) sit in this house
        occupants = [p.name for p in chart.planets.values() if p.house == house_num]
        occupant_str = ", ".join(occupants) if occupants else "no planets"

        # where the house's own lord is placed (classical technique: strength
        # of a house depends partly on where its lord sits)
        lord_house = None
        if lord in chart.planets:
            lord_house = chart.planets[lord].house

        fact_lines.append(
            f"{fact_num}. House number {house_num} has sign = {sign}, house lord = {lord}, "
            f"planets occupying house {house_num} = {occupant_str}."
            + (f" The lord {lord} itself sits in house number {lord_house}." if lord_house else "")
        )
        fact_num += 1
        query_fragments.append(f"{sign} in house {house_num} lord {lord}")
        if occupants:
            query_fragments.append(" ".join(occupants) + f" in house {house_num}")

    # Always mention Moon sign/nakshatra - central to most classical readings
    moon = chart.planets["Moon"]
    fact_lines.append(
        f"{fact_num}. Moon sign = {moon.sign}, Moon nakshatra (lunar mansion, NOT a house) = {moon.nakshatra}, "
        f"Moon is placed in house number {moon.house}."
    )
    query_fragments.append(f"Moon in {moon.sign} {moon.nakshatra}")

    return TopicRetrievalQuery(
        topic=topic,
        query_text=" ".join(query_fragments),
        chart_facts="\n".join(fact_lines),
    )


def build_narrative_prompt(topic: str, chart_facts: str, retrieved_chunks: list[dict]) -> str:
    if retrieved_chunks:
        context = "\n\n".join(
            f"[Source: {c['source_file']}, Page {c['page_number']}]\n{c['text']}"
            for c in retrieved_chunks
        )
    else:
        context = "(No closely matching passages were found in the text for this placement.)"

    return NARRATIVE_PROMPT_TEMPLATE.format(
        topic_label=TOPIC_LABELS[topic],
        chart_facts=chart_facts,
        context=context,
    )


def generate_topic_narrative(
    chart: BirthChart,
    topic: str,
    retriever,          # an instance of rag.retriever.Retriever
    llama_model,         # an already-loaded model, e.g. from get_llama_model(path)
    top_k: int = 5,
    max_new_tokens: int = 400,
    temperature: float = 0.4,
) -> dict:
    """
    Full pipeline for ONE topic: build query from real chart data -> retrieve
    from the book -> generate a grounded narrative paragraph.

    Returns a dict with the topic, the query used, the retrieved chunks (so
    the frontend/dashboard can show citations), and the generated text.
    """
    tq = build_topic_query(chart, topic)
    logger.info("Topic '%s' retrieval query: %s", topic, tq.query_text)

    retrieved_chunks = retriever.retrieve(tq.query_text, top_k=top_k)

    prompt = build_narrative_prompt(topic, tq.chart_facts, retrieved_chunks)

    logger.info("Generating narrative for topic '%s' (max_new_tokens=%d)...", topic, max_new_tokens)
    result = llama_model(
        prompt,
        max_tokens=max_new_tokens,
        temperature=temperature,
        top_p=0.9,
        repeat_penalty=1.3,
        echo=False,
        stop=["\n\nReal chart facts:", "\n\nWrite the prediction"],
    )
    narrative_text = result["choices"][0]["text"].strip()

    # Defensive check: some llama-cpp-python configurations/versions can end
    # up echoing the prompt back inside "text" regardless of the echo=False
    # flag above. If that happens, strip the prompt out rather than showing
    # the user their own input parroted back as a "prediction".
    if narrative_text.startswith(prompt.strip()[:200]):
        narrative_text = narrative_text[len(prompt):].strip()

    if not narrative_text:
        narrative_text = (
            "The model did not return a usable prediction for this topic "
            "(empty or echoed output). Try regenerating, or check the "
            "generation parameters/model call in narrative.py."
        )

    return {
        "topic": topic,
        "chart_facts": tq.chart_facts,
        "retrieval_query": tq.query_text,
        "retrieved_chunks": retrieved_chunks,
        "narrative": narrative_text,
    }


def generate_full_reading(
    chart: BirthChart,
    retriever,
    llama_model,
    topics: list[str] | None = None,
    top_k: int = 5,
    max_new_tokens: int = 400,
    temperature: float = 0.4,
) -> dict:
    """
    Runs generate_topic_narrative() across multiple topics and returns a
    combined dict keyed by topic. Defaults to all 5 implemented topics.

    NOTE: on a CPU-only 1B model, each topic generation can take roughly
    30-90 seconds. Five topics run sequentially means a few minutes total
    for a full reading - this is expected given the hardware, not a bug.
    """
    if topics is None:
        topics = list(TOPIC_HOUSES.keys())

    reading = {}
    for topic in topics:
        reading[topic] = generate_topic_narrative(
            chart, topic, retriever, llama_model,
            top_k=top_k, max_new_tokens=max_new_tokens, temperature=temperature,
        )
    return reading


# TODO: transits
# Monthly/yearly predictions require computing current (or a chosen date's)
# planetary positions via chart_calculator's same swisseph calls, comparing
# them against the natal chart (e.g. "transiting Saturn currently in natal
# house 8"), and building a similar topic query + narrative flow as above,
# but keyed to a time window rather than a static natal placement.


if __name__ == "__main__":
    # Smoke test for the query-building logic only (no retriever/model needed).
    from astro.chart_calculator import calculate_birth_chart

    chart = calculate_birth_chart(
        name="Test User",
        birth_date="1990-08-15",
        birth_time="14:30",
        utc_offset_hours=5.5,
        latitude=28.6139,
        longitude=77.2090,
        place_name="New Delhi, India",
    )

    for topic in TOPIC_HOUSES:
        tq = build_topic_query(chart, topic)
        print(f"\n=== {topic} ===")
        print("Query:", tq.query_text)
        print("Facts:\n", tq.chart_facts)