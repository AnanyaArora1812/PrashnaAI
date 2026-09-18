from __future__ import annotations

import logging
import os

from openai import OpenAI

from astro.narrative import build_topic_query, build_narrative_prompt, TOPIC_LABELS
from astro.chart_calculator import BirthChart

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = "openai/gpt-oss-120b"


def get_groq_client(api_key: str | None = None) -> OpenAI:
    key = api_key or os.environ.get("GROQ_API_KEY")
    if not key:
        raise RuntimeError(
            "No Groq API key found. Set it with:\n"
            '  $env:GROQ_API_KEY = "gsk_..."\n'
            "in PowerShell before running."
        )
    return OpenAI(api_key=key, base_url=GROQ_BASE_URL)


def generate_topic_narrative_groq(
    chart: BirthChart,
    topic: str,
    retriever,
    client: OpenAI | None = None,
    model: str = DEFAULT_MODEL,
    top_k: int = 5,
    temperature: float = 0.4,
) -> dict:
    if client is None:
        client = get_groq_client()

    tq = build_topic_query(chart, topic)
    logger.info("Topic '%s' retrieval query: %s", topic, tq.query_text)

    retrieved_chunks = retriever.retrieve(tq.query_text, top_k=top_k)
    prompt = build_narrative_prompt(topic, tq.chart_facts, retrieved_chunks)

    logger.info("Calling Groq (%s) for topic '%s'...", model, topic)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are PrashnaAI, a careful Vedic astrology assistant. "
                    "You only ever use the exact chart facts given to you - "
                    "you never invent or guess additional planetary placements."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )
    narrative_text = response.choices[0].message.content.strip()

    return {
        "topic": topic,
        "chart_facts": tq.chart_facts,
        "retrieval_query": tq.query_text,
        "retrieved_chunks": retrieved_chunks,
        "narrative": narrative_text,
        "backend": f"groq:{model}",
    }


def generate_full_reading_groq(
    chart: BirthChart,
    retriever,
    client: OpenAI | None = None,
    model: str = DEFAULT_MODEL,
    topics: list[str] | None = None,
    top_k: int = 5,
    temperature: float = 0.4,
) -> dict:
    if client is None:
        client = get_groq_client()
    if topics is None:
        topics = list(TOPIC_LABELS.keys())

    reading = {}
    for topic in topics:
        reading[topic] = generate_topic_narrative_groq(
            chart, topic, retriever, client=client, model=model,
            top_k=top_k, temperature=temperature,
        )
    return reading