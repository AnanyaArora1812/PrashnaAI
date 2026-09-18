"""
numerology.py

Simple deterministic numerology from date of birth. Pure arithmetic - no AI,
no external calls. This mirrors the standard Vedic/Indian numerology system
(distinct from Western Pythagorean/Chaldean name-numerology, which is not
implemented here since the brief only asked for DOB-based numbers).

Mulyank (मूलांक, "root number"): derived from the day of birth only, reduced
to a single digit 1-9. Governs day-to-day personality traits.

Bhagyank (भाग्यांक, "destiny/life-path number"): derived from the FULL date
of birth (day + month + year), reduced to a single digit 1-9. Governs the
overall life path.

Both numbers are traditionally each ruled by a planet:
    1 -> Sun      2 -> Moon      3 -> Jupiter   4 -> Rahu (Uranus in Western)
    5 -> Mercury  6 -> Venus     7 -> Ketu (Neptune in Western)
    8 -> Saturn   9 -> Mars

Master numbers (11, 22) are NOT collapsed further in some numerology schools;
this implementation reduces everything down to 1-9 by default (the more
common convention in Indian numerology), but keeps the pre-reduction
intermediate sum available for anyone who wants to check for repeating/
master digits themselves.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


PLANET_RULERS = {
    1: "Sun",
    2: "Moon",
    3: "Jupiter",
    4: "Rahu",
    5: "Mercury",
    6: "Venus",
    7: "Ketu",
    8: "Saturn",
    9: "Mars",
}

# Lucky-number and lucky-color associations are a common (though not
# universally agreed-upon) convention in Indian numerology, keyed by the
# ruling planet of the Mulyank. Treat these as illustrative content for the
# narrative layer, not as fixed astronomical facts.
LUCKY_ASSOCIATIONS = {
    "Sun": {
        "numbers": [1, 10, 19, 28],
        "colors": ["Orange", "Red", "Gold"],
        "colors_hindi": ["नारंगी", "लाल", "सुनहरा"],
    },
    "Moon": {
        "numbers": [2, 11, 20, 29],
        "colors": ["White", "Cream", "Silver"],
        "colors_hindi": ["सफेद", "क्रीम", "चांदी"],
    },
    "Jupiter": {
        "numbers": [3, 12, 21, 30],
        "colors": ["Yellow", "Gold"],
        "colors_hindi": ["पीला", "सुनहरा"],
    },
    "Rahu": {
        "numbers": [4, 13, 22, 31],
        "colors": ["Grey", "Smoky blue", "Electric blue"],
        "colors_hindi": ["स्लेटी", "धुएँ जैसा नीला"],
    },
    "Mercury": {
        "numbers": [5, 14, 23],
        "colors": ["Green"],
        "colors_hindi": ["हरा"],
    },
    "Venus": {
        "numbers": [6, 15, 24],
        "colors": ["Pastel shades", "White", "Pink"],
        "colors_hindi": ["हल्का गुलाबी", "सफेद"],
    },
    "Ketu": {
        "numbers": [7, 16, 25],
        "colors": ["Grey", "Brown", "Multi-colored"],
        "colors_hindi": ["स्लेटी", "भूरा"],
    },
    "Saturn": {
        "numbers": [8, 17, 26],
        "colors": ["Dark blue", "Black"],
        "colors_hindi": ["गहरा नीला", "काला"],
    },
    "Mars": {
        "numbers": [9, 18, 27],
        "colors": ["Red"],
        "colors_hindi": ["लाल"],
    },
}


def _digit_sum(n: int) -> int:
    return sum(int(d) for d in str(abs(n)))


def _reduce_to_single_digit(n: int) -> int:
    while n > 9:
        n = _digit_sum(n)
    return n


@dataclass
class NumerologyProfile:
    mulyank: int
    mulyank_ruler: str
    bhagyank: int
    bhagyank_ruler: str
    lucky_numbers: list
    lucky_colors: list
    lucky_colors_hindi: list

    def as_dict(self) -> dict:
        return {
            "mulyank": self.mulyank,
            "mulyank_ruler": self.mulyank_ruler,
            "bhagyank": self.bhagyank,
            "bhagyank_ruler": self.bhagyank_ruler,
            "lucky_numbers": self.lucky_numbers,
            "lucky_colors": self.lucky_colors,
            "lucky_colors_hindi": self.lucky_colors_hindi,
        }


def calculate_mulyank(birth_date: date) -> int:
    """Root number - single-digit reduction of the day of birth only."""
    return _reduce_to_single_digit(birth_date.day)


def calculate_bhagyank(birth_date: date) -> int:
    """Destiny number - single-digit reduction of the full DD+MM+YYYY sum."""
    total = (
        _digit_sum(birth_date.day)
        + _digit_sum(birth_date.month)
        + _digit_sum(birth_date.year)
    )
    return _reduce_to_single_digit(total)


def calculate_numerology(birth_date_str: str) -> NumerologyProfile:
    """
    birth_date_str: "YYYY-MM-DD"
    """
    y, m, d = (int(x) for x in birth_date_str.split("-"))
    birth_date = date(y, m, d)

    mulyank = calculate_mulyank(birth_date)
    bhagyank = calculate_bhagyank(birth_date)

    mulyank_ruler = PLANET_RULERS[mulyank]
    bhagyank_ruler = PLANET_RULERS[bhagyank]

    lucky = LUCKY_ASSOCIATIONS[mulyank_ruler]

    return NumerologyProfile(
        mulyank=mulyank,
        mulyank_ruler=mulyank_ruler,
        bhagyank=bhagyank,
        bhagyank_ruler=bhagyank_ruler,
        lucky_numbers=lucky["numbers"],
        lucky_colors=lucky["colors"],
        lucky_colors_hindi=lucky["colors_hindi"],
    )


if __name__ == "__main__":
    profile = calculate_numerology("1990-08-15")
    import json
    print(json.dumps(profile.as_dict(), indent=2, ensure_ascii=False))