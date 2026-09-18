"""
narrative_openai.py

Cloud-based alternative to narrative.py's local LLaMA generation. Reuses the
exact same retrieval-query-building and chart-fact-grounding logic from
narrative.py - the ONLY thing that changes is which model writes the final
paragraph. The chart facts and retrieved book passages are still assembled
from real computed data, never invented by the API.

SECURITY: the API key is read from an environment variable, never hardcoded.
Set it before running (PowerShell):
    $env:OPENAI_API_KEY = "sk-..."
Or, for something that persists across terminal sessions, set it as a
permanent Windows environment variable via System Properties > Environment
Variables, so you don't have to retype it every time.

NEVER put the actual key value inside any .py file or commit it to GitHub.
If a key was ever pasted into a chat, file, or committed to a public repo,
treat it as compromised and revoke/regenerate it at platform.openai.com.

Install:
    pip install openai
"""

from __future__ import annotations

import logging
import os

from openai import OpenAI

from astro.narrative import build_topic_query, build_narrative_prompt, TOPIC_LABELS
from astro.chart_calculator import BirthChart

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_openai_client(api_key: str | None = None) -> OpenAI:
    """
    Reads the key from the OPENAI_API_KEY environment variable by default.
    Pass api_key explicitly only for one-off testing - never hardcode it
    in a file you might commit or share.
    """
    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "No OpenAI API key found. Set it with:\n"
            '  $env:OPENAI_API_KEY = "sk-..."\n'
            "in PowerShell before running, or pass api_key= explicitly for a one-off test."
        )
    return OpenAI(api_key=key)


def generate_topic_narrative_openai(
    chart: BirthChart,
    topic: str,
    retriever,               # rag.retriever.Retriever instance
    client: OpenAI | None = None,
    model: str = "gpt-4o-mini",
    top_k: int = 5,
    temperature: float = 0.4,
) -> dict:
    """
    Same interface/shape of result as narrative.generate_topic_narrative(),
    but generation happens via the OpenAI API instead of local LLaMA.

    model: "gpt-4o-mini" is a reasonable default - noticeably better quality
    than gpt-3.5-turbo and cheaper per request. Change if you prefer another.
    """
    if client is None:
        client = get_openai_client()

    tq = build_topic_query(chart, topic)
    logger.info("Topic '%s' retrieval query: %s", topic, tq.query_text)

    retrieved_chunks = retriever.retrieve(tq.query_text, top_k=top_k)
    prompt = build_narrative_prompt(topic, tq.chart_facts, retrieved_chunks)

    logger.info("Calling OpenAI (%s) for topic '%s'...", model, topic)
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
        "backend": f"openai:{model}",
    }


def generate_full_reading_openai(
    chart: BirthChart,
    retriever,
    client: OpenAI | None = None,
    model: str = "gpt-4o-mini",
    topics: list[str] | None = None,
    top_k: int = 5,
    temperature: float = 0.4,
) -> dict:
    if client is None:
        client = get_openai_client()
    if topics is None:
        topics = list(TOPIC_LABELS.keys())

    reading = {}
    for topic in topics:
        reading[topic] = generate_topic_narrative_openai(
            chart, topic, retriever, client=client, model=model,
            top_k=top_k, temperature=temperature,
        )
    return reading