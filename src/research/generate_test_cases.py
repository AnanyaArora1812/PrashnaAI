"""
generate_test_cases.py

Generates 50 REPRODUCIBLE synthetic test cases (name, DOB, TOB, place) for
the Generic vs Adaptive comparison experiment. Fixed random seed so the
exact same 50 cases can be regenerated later (important for a research
paper - a reviewer or you yourself should be able to reproduce this run).

Cities are restricted to ones geocoding.py's offline dataset resolves
reliably (per the known limitation noted elsewhere in this project - major
international cities aren't all well-covered, Indian cities are).
"""

import json
import random
from pathlib import Path

random.seed(42)  # fixed seed = reproducible test set, cite this in the paper

CITIES = [
    "Kanpur", "Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata",
    "Hyderabad", "Pune", "Jaipur", "Lucknow", "Varanasi", "Patna",
    "Bhopal", "Indore", "Nagpur", "Surat", "Ahmedabad", "Chandigarh",
    "Amritsar", "Guwahati",
]

TOPICS = ["career", "finance", "family", "relationships", "personality"]

OUTPUT_PATH = Path("src/research/test_cases.json")


def generate_test_cases(n: int = 50) -> list[dict]:
    cases = []
    for i in range(1, n + 1):
        year = random.randint(1970, 2005)
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # 28 avoids month-length edge cases entirely
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)

        cases.append({
            "case_id": i,
            "name": f"Test User {i:02d}",
            "birth_date": f"{year:04d}-{month:02d}-{day:02d}",
            "birth_time": f"{hour:02d}:{minute:02d}",
            "place": random.choice(CITIES),
            "topic": TOPICS[(i - 1) % len(TOPICS)],  # cycles evenly through all 5 topics
        })
    return cases


if __name__ == "__main__":
    cases = generate_test_cases(50)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)
    print(f"Generated {len(cases)} test cases -> {OUTPUT_PATH}")