"""
run_comparison_benchmark.py

Runs all 50 test cases through TWO conditions, both using 100% real
astronomical calculation - nothing hallucinated in either:

  GENERIC: uses only Sun sign + Moon sign (real, calculated) - the depth
  a newspaper horoscope column would use. No book retrieval, no house-level
  facts. Isolates "shallow real data, no grounding" as the baseline.

  ADAPTIVE: uses the full real chart (all planets/houses/nakshatras) PLUS
  RAG retrieval from the actual classical text - the system this whole
  project builds toward.

  Both conditions call the SAME Groq model, so the comparison isolates the
  effect of chart depth + retrieval grounding, not a difference in LLM.

Records exactly the 4 metrics requested: response_time, failed,
processing_time, output_generation_time - for every case x condition.
"""

from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import OpenAI

from astro.geocoding import resolve_place, PlaceNotFoundError, AmbiguousPlaceError
from astro.chart_calculator import calculate_birth_chart
from astro.narrative import build_topic_query, build_narrative_prompt
from astro.narrative_groq import get_groq_client, DEFAULT_MODEL
from rag.retriever import Retriever

TEST_CASES_PATH = Path(__file__).parent / "test_cases.json"
RESULTS_CSV_PATH = Path(__file__).parent / "benchmark_results.csv"
RESULTS_JSON_PATH = Path(__file__).parent / "benchmark_results_full.json"  # includes raw output text, for the human-eval step

FAISS_INDEX_PATH = "datasets/processed/faiss_index/index.faiss"
FAISS_METADATA_PATH = "datasets/processed/faiss_index/metadata.json"
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Small delay between Groq calls to reduce 429 rate-limit churn (same
# lesson learned from the monthly-transit timing test earlier in this
# project) - a fixed delay is more predictable for a paper's timing numbers
# than letting exponential backoff retries dominate the measurement.
DELAY_BETWEEN_CALLS_SECONDS = 3

GENERIC_SYSTEM_PROMPT = (
    "You are an astrologer writing a brief, general horoscope reading, "
    "the way a newspaper horoscope column would - based only on the two "
    "zodiac signs given, with no other chart details available."
)

GENERIC_PROMPT_TEMPLATE = """Write a general {topic_label} reading for someone with:
- Sun sign: {sun_sign}
- Moon sign: {moon_sign}

Write 3-5 sentences, readable and generally applicable to anyone with this Sun/Moon combination."""

TOPIC_LABELS_LOCAL = {
    "career": "career and professional life",
    "finance": "financial stability and wealth",
    "family": "family and domestic life",
    "relationships": "relationships and marriage",
    "personality": "core personality and nature",
}


def run_generic(chart, topic: str, client: OpenAI) -> dict:
    """Generic condition: real Sun/Moon signs only, no retrieval."""
    t0 = time.time()
    prompt = GENERIC_PROMPT_TEMPLATE.format(
        topic_label=TOPIC_LABELS_LOCAL[topic],
        sun_sign=chart.sun_sign(),
        moon_sign=chart.moon_sign(),
    )
    t1 = time.time()  # end of "processing" (trivial here - just string formatting)

    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": GENERIC_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )
        output_text = response.choices[0].message.content.strip()
        t2 = time.time()
        return {
            "failed": False,
            "processing_time_s": round(t1 - t0, 3),
            "output_generation_time_s": round(t2 - t1, 3),
            "response_time_s": round(t2 - t0, 3),
            "output_text": output_text,
            "error": None,
        }
    except Exception as e:
        t2 = time.time()
        return {
            "failed": True,
            "processing_time_s": round(t1 - t0, 3),
            "output_generation_time_s": round(t2 - t1, 3),
            "response_time_s": round(t2 - t0, 3),
            "output_text": "",
            "error": str(e),
        }
        

def run_adaptive(chart, topic: str, retriever: Retriever, client: OpenAI) -> dict:
    """Adaptive condition: full real chart facts + RAG retrieval."""
    t0 = time.time()
    try:
        tq = build_topic_query(chart, topic)
        retrieved_chunks = retriever.retrieve(tq.query_text, top_k=8)
        prompt = build_narrative_prompt(topic, tq.chart_facts, retrieved_chunks)
        t1 = time.time()  # end of processing (chart facts + retrieval)

        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are PrashnaAI, a careful Vedic astrology assistant. "
                        "You only ever use the exact chart facts given to you."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )
        output_text = response.choices[0].message.content.strip()
        t2 = time.time()
        return {
            "failed": False,
            "processing_time_s": round(t1 - t0, 3),
            "output_generation_time_s": round(t2 - t1, 3),
            "response_time_s": round(t2 - t0, 3),
            "output_text": output_text,
            "error": None,
        }
    except Exception as e:
        t_fail = time.time()
        return {
            "failed": True,
            "processing_time_s": round(t_fail - t0, 3),
            "output_generation_time_s": 0.0,
            "response_time_s": round(t_fail - t0, 3),
            "output_text": "",
            "error": str(e),
        }


def main() -> None:
    with open(TEST_CASES_PATH, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    print(f"Loaded {len(test_cases)} test cases.")
    print("Loading retriever...")
    retriever = Retriever(
        index_path=FAISS_INDEX_PATH,
        metadata_path=FAISS_METADATA_PATH,
        embedding_model_name=EMBEDDING_MODEL_NAME,
    )
    client = get_groq_client()

    all_results = []

    for case in test_cases:
        print(f"\n[Case {case['case_id']}/{len(test_cases)}] {case['name']} - {case['place']} - topic: {case['topic']}")

        try:
            location = resolve_place(case["place"], birth_date=case["birth_date"])
            chart = calculate_birth_chart(
                name=case["name"],
                birth_date=case["birth_date"],
                birth_time=case["birth_time"],
                utc_offset_hours=location.utc_offset_hours,
                latitude=location.latitude,
                longitude=location.longitude,
                place_name=case["place"],
            )
        except (PlaceNotFoundError, AmbiguousPlaceError, Exception) as e:
            print(f"  SKIPPED (chart/geocoding failed): {e}")
            all_results.append({
                "case_id": case["case_id"], "condition": "generic",
                "failed": True, "processing_time_s": 0, "output_generation_time_s": 0,
                "response_time_s": 0, "output_text": "", "error": f"chart_calc_failed: {e}",
                "topic": case["topic"],
            })
            all_results.append({
                "case_id": case["case_id"], "condition": "adaptive",
                "failed": True, "processing_time_s": 0, "output_generation_time_s": 0,
                "response_time_s": 0, "output_text": "", "error": f"chart_calc_failed: {e}",
                "topic": case["topic"],
            })
            continue

        generic_result = run_generic(chart, case["topic"], client)
        print(f"  GENERIC:  {generic_result['response_time_s']}s (failed={generic_result['failed']})")
        generic_result.update({"case_id": case["case_id"], "condition": "generic", "topic": case["topic"]})
        all_results.append(generic_result)
        time.sleep(DELAY_BETWEEN_CALLS_SECONDS)

        adaptive_result = run_adaptive(chart, case["topic"], retriever, client)
        print(f"  ADAPTIVE: {adaptive_result['response_time_s']}s (failed={adaptive_result['failed']})")
        adaptive_result.update({"case_id": case["case_id"], "condition": "adaptive", "topic": case["topic"]})
        all_results.append(adaptive_result)
        time.sleep(DELAY_BETWEEN_CALLS_SECONDS)

    # ---- Save full results (with output text) for the human-eval step ----
    with open(RESULTS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    # ---- Save a clean CSV (no output text) for the paper's timing table ----
    with open(RESULTS_CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "case_id", "condition", "topic", "failed",
            "processing_time_s", "output_generation_time_s", "response_time_s", "error",
        ])
        writer.writeheader()
        for r in all_results:
            writer.writerow({k: r.get(k, "") for k in writer.fieldnames})

    print_summary(all_results)
    print(f"\nFull results (with text, for human eval): {RESULTS_JSON_PATH}")
    print(f"Timing table (for paper): {RESULTS_CSV_PATH}")


def print_summary(all_results: list[dict]) -> None:
    import statistics

    print("\n" + "=" * 60)
    print("SUMMARY: Generic vs Adaptive")
    print("=" * 60)

    for condition in ["generic", "adaptive"]:
        rows = [r for r in all_results if r["condition"] == condition]
        ok_rows = [r for r in rows if not r["failed"]]
        n_failed = len(rows) - len(ok_rows)

        print(f"\n--- {condition.upper()} ---")
        print(f"  n = {len(rows)}, failed = {n_failed} ({n_failed/len(rows)*100:.1f}%)")

        if ok_rows:
            resp = [r["response_time_s"] for r in ok_rows]
            proc = [r["processing_time_s"] for r in ok_rows]
            gen = [r["output_generation_time_s"] for r in ok_rows]
            print(f"  avg response_time:    {statistics.mean(resp):.2f}s (median {statistics.median(resp):.2f}s)")
            print(f"  avg processing_time:  {statistics.mean(proc):.2f}s")
            print(f"  avg generation_time:  {statistics.mean(gen):.2f}s")


if __name__ == "__main__":
    main()