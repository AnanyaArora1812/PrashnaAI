"""
monthly_narrative.py

Turns real transit data (transit_calculator.py) into month-by-month readings:
overview, do's, don'ts, likely problems, how to handle them, closing advice.

Same architecture discipline as narrative.py/narrative_groq.py: the LLM never
invents a planetary fact. Every prompt states the real transiting positions,
real natal house they fall into, and real classical events (ingresses,
retrograde stations, Sade Sati) that happened that specific month. The LLM's
only job is turning [real transit facts + real natal facts + real book text]
into a readable, specific, actionable monthly reading - not generating
astrology from nothing.

Reuses the existing Retriever and Groq client setup from narrative_groq.py -
this module doesn't reinvent either of those, just a new fact-builder and
prompt template aimed at the monthly/transit use case instead of the
static-natal-topic use case.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from openai import OpenAI

from astro.chart_calculator import BirthChart
from astro.transit_calculator import MonthlyTransit, MONTHLY_RELEVANT_PLANETS

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


MONTHLY_SYSTEM_PROMPT = (
    "You are PrashnaAI, a senior Vedic astrologer and numerologist with decades "
    "of practical consultation experience. People come to you for real, specific, "
    "usable monthly guidance - not vague generalities. You only ever reason from "
    "the exact transit and natal facts given to you; you never invent a planetary "
    "position, house, or event that wasn't stated."
)

MONTHLY_PROMPT_TEMPLATE = """Give this person their reading for {month_label}, based on the REAL transiting planetary positions this month and their REAL natal chart, plus REAL passages from a classical text (Brihat Parashar Hora Shastra) where relevant.

Grounding rules (these override everything else - never break them):
- Treat "This month's real transit facts" as ground truth. Never invent a planetary position, house, ingress, or retrograde station beyond what is listed.
- Use the "Reference passages" only if actually relevant to the facts given. If not relevant, rely on the transit/natal facts and general classical principles.
- Do not invent specific events (e.g. "you will get a job offer on the 14th") - speak in terms of tendencies, likely pressures, and openings, the way a responsible astrologer actually does.
- When you connect a transit to an effect, SHOW THE REASONING explicitly - name the transiting planet, the natal house/planet it's interacting with, and why that combination produces the effect you're describing. Do not just assert an outcome with no chain of logic.

Required structure - use these exact section headers:

**Overview**
2-3 sentences naming the overall theme/mood of this month for this person, based on what's actually moving.

**Do's**
3-4 concrete, specific actions or attitudes to lean into this month, each tied to an actual transit fact - not generic advice that could apply to any month.

**Don'ts**
3-4 concrete things to avoid or be cautious of this month, same standard - tied to a real transit fact, with the reasoning shown.

**Possible Challenges**
2-3 specific tensions or friction points likely this month, with the astrological reasoning spelled out (transiting planet X interacting with natal placement Y produces Z kind of pressure).

**How to Handle It**
For each challenge above, a concrete, practical way to work with it - not "stay positive," but an actual approach a person could use.

**Closing Advice**
2-3 warm, encouraging sentences to end on, grounded in what's genuinely supportive this month (not just generic positivity).

This month's real transit facts:
{transit_facts}

This person's relevant natal chart facts:
{natal_facts}

Reference passages from the classical text:
{context}

Write the full monthly reading now, following the required structure exactly, staying strictly consistent with the facts above:"""


@dataclass
class MonthlyRetrievalQuery:
    month_label: str
    query_text: str
    transit_facts: str
    natal_facts: str


def build_monthly_facts(natal_chart: BirthChart, transit: MonthlyTransit) -> MonthlyRetrievalQuery:
    """
    Turns a computed MonthlyTransit + the person's natal chart into:
      - a natural-language retrieval query to search the book with
      - a plain-language statement of the real transit facts for this month
      - a plain-language statement of the relevant natal facts to interpret against
    """
    fact_lines = []
    query_fragments = []

    for pname in MONTHLY_RELEVANT_PLANETS:
        p = transit.planets[pname]
        retro_note = " (retrograde)" if p.retrograde else ""
        fact_lines.append(
            f"- {pname} is transiting {p.sign}, falling in this person's natal house {p.house}{retro_note}."
        )
        query_fragments.append(f"{pname} transit house {p.house} {p.sign}")

    if transit.ingresses:
        fact_lines.append("- Sign changes (ingresses) happening this month: " + "; ".join(transit.ingresses) + ".")
        query_fragments.extend(transit.ingresses)

    if transit.stations:
        fact_lines.append("- Retrograde/direct stations this month: " + "; ".join(transit.stations) + ".")
        query_fragments.extend(transit.stations)

    if transit.sade_sati_phase:
        fact_lines.append(f"- This person is currently in Sade Sati: {transit.sade_sati_phase}.")
        query_fragments.append(f"Sade Sati {transit.sade_sati_phase} Saturn")

    natal_lines = [
        f"- Natal ascendant (Lagna) = {natal_chart.ascendant_sign}.",
        f"- Natal Moon sign = {natal_chart.moon_sign()}, natal Moon nakshatra = {natal_chart.moon_nakshatra()}.",
    ]

    return MonthlyRetrievalQuery(
        month_label=transit.month_label,
        query_text=" ".join(query_fragments) if query_fragments else f"transits {transit.month_label}",
        transit_facts="\n".join(fact_lines),
        natal_facts="\n".join(natal_lines),
    )


def build_monthly_prompt(mq: MonthlyRetrievalQuery, retrieved_chunks: list[dict]) -> str:
    if retrieved_chunks:
        context = "\n\n".join(
            f"[Source: {c['source_file']}, Page {c['page_number']}]\n{c['text']}"
            for c in retrieved_chunks
        )
    else:
        context = "(No closely matching passages were found in the text for this month's specific transits.)"

    return MONTHLY_PROMPT_TEMPLATE.format(
        month_label=mq.month_label,
        transit_facts=mq.transit_facts,
        natal_facts=mq.natal_facts,
        context=context,
    )


def generate_monthly_narrative_groq(
    natal_chart: BirthChart,
    transit: MonthlyTransit,
    retriever,
    client: OpenAI | None = None,
    model: str = DEFAULT_MODEL,
    top_k: int = 5,
    temperature: float = 0.5,
) -> dict:
    """One month's full reading: build query -> retrieve -> generate."""
    if client is None:
        client = get_groq_client()

    mq = build_monthly_facts(natal_chart, transit)
    logger.info("Month '%s' retrieval query: %s", mq.month_label, mq.query_text)

    retrieved_chunks = retriever.retrieve(mq.query_text, top_k=top_k)
    prompt = build_monthly_prompt(mq, retrieved_chunks)

    logger.info("Calling Groq (%s) for month '%s'...", model, mq.month_label)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": MONTHLY_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )
    narrative_text = response.choices[0].message.content.strip()

    return {
        "month_label": mq.month_label,
        "period_start": transit.period_start.isoformat(),
        "period_end": transit.period_end.isoformat(),
        "transit_facts": mq.transit_facts,
        "natal_facts": mq.natal_facts,
        "retrieval_query": mq.query_text,
        "retrieved_chunks": retrieved_chunks,
        "ingresses": transit.ingresses,
        "stations": transit.stations,
        "sade_sati_phase": transit.sade_sati_phase,
        "narrative": narrative_text,
        "backend": f"groq:{model}",
    }


def generate_full_year_forecast_groq(
    natal_chart: BirthChart,
    monthly_transits: list[MonthlyTransit],
    retriever,
    client: OpenAI | None = None,
    model: str = DEFAULT_MODEL,
    top_k: int = 5,
    temperature: float = 0.5,
) -> list[dict]:
    """
    Runs generate_monthly_narrative_groq() across all 12 (or however many)
    months. Returns a list in chronological order, ready for the frontend
    to render directly without further reordering/lookup.
    """
    if client is None:
        client = get_groq_client()

    forecast = []
    for transit in monthly_transits:
        forecast.append(
            generate_monthly_narrative_groq(
                natal_chart, transit, retriever, client=client,
                model=model, top_k=top_k, temperature=temperature,
            )
        )
    return forecast