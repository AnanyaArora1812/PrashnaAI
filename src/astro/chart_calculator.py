"""
chart_calculator.py

Deterministic Vedic (sidereal) birth chart calculation using the Swiss Ephemeris.

This module is intentionally free of any LLM/AI code. It computes real planetary
positions, houses, and divisional charts from date/time/place of birth. The output
of this module is what later gets handed to the RAG + LLaMA narrative layer -
never the other way around. The LLM should never be asked to "generate" a chart.

Ayanamsa: Lahiri (Chitrapaksha) - the standard used by the Indian government's
official Rashtriya Panchang and by most Vedic astrology software.

House system: Whole Sign (the classical Vedic method - the sign containing the
ascendant degree becomes the whole 1st house, next sign the whole 2nd house, etc.)
This is different from Western Placidus/Equal house systems.

Dependencies:
    pip install pyswisseph      (Python <= 3.11 on Windows: prebuilt wheel exists)
    pip install pysweph         (Python >= 3.12 on Windows: prebuilt wheel exists,
                                  drop-in replacement, still `import swisseph as swe`)

No internet access needed at runtime. Swiss Ephemeris ships its own internal
"Moshier" analytical ephemeris that's accurate enough for this use case (arc-second
level) without downloading separate .se1 ephemeris data files.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import swisseph as swe

# ---------------------------------------------------------------------------
# Static reference data
# ---------------------------------------------------------------------------

RASHIS = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena",
]

RASHI_HINDI = [
    "मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या",
    "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन",
]

RASHI_LORDS = [
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter",
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

# Nakshatra lords cycle in the standard Vimshottari order, repeating every 9
NAKSHATRA_LORDS_CYCLE = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury",
]

PLANET_IDS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.TRUE_NODE,   # Rahu = True Lunar North Node
    # Ketu is always exactly 180 degrees from Rahu, computed manually below
}

SIGN_SPAN = 30.0          # degrees per rashi
NAKSHATRA_SPAN = 360.0 / 27.0   # 13.333... degrees per nakshatra
PADA_SPAN = NAKSHATRA_SPAN / 4  # each nakshatra has 4 padas


# ---------------------------------------------------------------------------
# Data classes for structured output
# ---------------------------------------------------------------------------

@dataclass
class PlanetPosition:
    name: str
    longitude: float          # sidereal longitude, 0-360
    sign_index: int            # 0=Mesha ... 11=Meena
    sign: str
    sign_hindi: str
    degree_in_sign: float      # 0-30, position within the sign
    nakshatra: str
    nakshatra_lord: str
    pada: int                  # 1-4
    house: int                 # 1-12, relative to ascendant (whole sign)
    retrograde: bool

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "longitude": round(self.longitude, 4),
            "sign": self.sign,
            "sign_hindi": self.sign_hindi,
            "degree_in_sign": round(self.degree_in_sign, 2),
            "nakshatra": self.nakshatra,
            "nakshatra_lord": self.nakshatra_lord,
            "pada": self.pada,
            "house": self.house,
            "retrograde": self.retrograde,
        }


@dataclass
class BirthChart:
    name: str
    birth_datetime_local: datetime
    utc_offset_hours: float
    latitude: float
    longitude: float
    place_name: str

    ascendant_longitude: float
    ascendant_sign_index: int
    ascendant_sign: str
    ascendant_sign_hindi: str

    planets: dict = field(default_factory=dict)          # name -> PlanetPosition (D1 / Rashi chart)
    navamsa_planets: dict = field(default_factory=dict)  # name -> PlanetPosition (D9 chart, house field = navamsa sign index+1)

    def moon_sign(self) -> str:
        return self.planets["Moon"].sign

    def moon_nakshatra(self) -> str:
        return self.planets["Moon"].nakshatra

    def sun_sign(self) -> str:
        return self.planets["Sun"].sign

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "birth_datetime_local": self.birth_datetime_local.isoformat(),
            "utc_offset_hours": self.utc_offset_hours,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "place_name": self.place_name,
            "ascendant": {
                "longitude": round(self.ascendant_longitude, 4),
                "sign": self.ascendant_sign,
                "sign_hindi": self.ascendant_sign_hindi,
            },
            "rashi_chart": {name: p.as_dict() for name, p in self.planets.items()},
            "navamsa_chart": {name: p.as_dict() for name, p in self.navamsa_planets.items()},
        }


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _sign_index(longitude: float) -> int:
    return int(math.floor(longitude / SIGN_SPAN)) % 12


def _nakshatra_index(longitude: float) -> int:
    return int(math.floor(longitude / NAKSHATRA_SPAN)) % 27


def _pada(longitude: float) -> int:
    position_in_nakshatra = longitude % NAKSHATRA_SPAN
    return int(math.floor(position_in_nakshatra / PADA_SPAN)) + 1


def _house_from_ascendant(planet_sign_index: int, asc_sign_index: int) -> int:
    """Whole-sign house: house number = how many signs ahead of the ascendant sign."""
    return ((planet_sign_index - asc_sign_index) % 12) + 1


def _navamsa_sign_index(longitude: float) -> int:
    """
    D9 / Navamsa calculation.

    Each 30-degree sign is divided into 9 navamsa parts of 3°20' each.
    The navamsa sign sequence depends on the element of the birth sign:
      - Movable (Mesha, Karka, Tula, Makara): navamsas start counting from the
        same sign.
      - Fixed (Vrishabha, Simha, Vrishchika, Kumbha): navamsas start counting
        from the 9th sign from it.
      - Dual (Mithuna, Kanya, Dhanu, Meena): navamsas start counting from the
        5th sign from it.
    """
    sign_index = _sign_index(longitude)
    position_in_sign = longitude % SIGN_SPAN
    navamsa_part = int(math.floor(position_in_sign / (SIGN_SPAN / 9)))  # 0-8

    element = sign_index % 3  # 0=movable, 1=fixed, 2=dual (Mesha=0 movable, Vrishabha=1 fixed, Mithuna=2 dual...)
    if element == 0:      # movable
        start_sign = sign_index
    elif element == 1:    # fixed
        start_sign = (sign_index + 8) % 12   # 9th sign from it (0-indexed offset of 8)
    else:                 # dual
        start_sign = (sign_index + 4) % 12   # 5th sign from it (0-indexed offset of 4)

    return (start_sign + navamsa_part) % 12


def _build_planet_position(
    name: str,
    longitude: float,
    asc_sign_index: int,
    retrograde: bool,
) -> PlanetPosition:
    sign_idx = _sign_index(longitude)
    nak_idx = _nakshatra_index(longitude)
    return PlanetPosition(
        name=name,
        longitude=longitude,
        sign_index=sign_idx,
        sign=RASHIS[sign_idx],
        sign_hindi=RASHI_HINDI[sign_idx],
        degree_in_sign=longitude % SIGN_SPAN,
        nakshatra=NAKSHATRAS[nak_idx],
        nakshatra_lord=NAKSHATRA_LORDS_CYCLE[nak_idx % 9],
        pada=_pada(longitude),
        house=_house_from_ascendant(sign_idx, asc_sign_index),
        retrograde=retrograde,
    )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def calculate_birth_chart(
    name: str,
    birth_date: str,       # "YYYY-MM-DD"
    birth_time: str,       # "HH:MM" 24-hour, LOCAL time at birth place
    utc_offset_hours: float,   # e.g. 5.5 for IST
    latitude: float,
    longitude: float,
    place_name: str = "",
    ayanamsa: int = swe.SIDM_LAHIRI,
) -> BirthChart:
    """
    Compute a full sidereal Vedic birth chart (Rashi/D1 + Navamsa/D9) from
    exact birth date, time, timezone offset, and coordinates.

    latitude: positive = North, negative = South
    longitude: positive = East, negative = West
    """
    swe.set_sid_mode(ayanamsa)

    dt_local = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
    hour_local_decimal = dt_local.hour + dt_local.minute / 60.0 + dt_local.second / 3600.0
    hour_ut = hour_local_decimal - utc_offset_hours

    jd_ut = swe.julday(dt_local.year, dt_local.month, dt_local.day, hour_ut)

    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    # Ascendant + houses (whole sign, but we only actually need the ascendant
    # degree itself since Vedic whole-sign houses are derived from its sign)
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=flags)
    asc_longitude = ascmc[0]
    asc_sign_index = _sign_index(asc_longitude)

    planets: dict[str, PlanetPosition] = {}
    navamsa_planets: dict[str, PlanetPosition] = {}

    raw_longitudes: dict[str, float] = {}

    for pname, pid in PLANET_IDS.items():
        calc_result = swe.calc_ut(jd_ut, pid, flags)
        # Some builds of the swisseph bindings (e.g. the pysweph fork) return
        # a 3rd element (an info/error string about which ephemeris file was
        # used); the original pyswisseph returns just 2. Handle both safely.
        result = calc_result[0]
        lon = result[0] % 360.0
        speed = result[3]
        retrograde = speed < 0
        raw_longitudes[pname] = lon
        planets[pname] = _build_planet_position(pname, lon, asc_sign_index, retrograde)
        nav_sign_idx = _navamsa_sign_index(lon)
        navamsa_planets[pname] = PlanetPosition(
            name=pname,
            longitude=lon,
            sign_index=nav_sign_idx,
            sign=RASHIS[nav_sign_idx],
            sign_hindi=RASHI_HINDI[nav_sign_idx],
            degree_in_sign=lon % SIGN_SPAN,
            nakshatra=planets[pname].nakshatra,
            nakshatra_lord=planets[pname].nakshatra_lord,
            pada=planets[pname].pada,
            house=_house_from_ascendant(nav_sign_idx, _navamsa_sign_index(asc_longitude)),
            retrograde=retrograde,
        )

    # Ketu = Rahu + 180 degrees, always retrograde, no independent speed calc needed
    rahu_lon = raw_longitudes["Rahu"]
    ketu_lon = (rahu_lon + 180.0) % 360.0
    planets["Ketu"] = _build_planet_position("Ketu", ketu_lon, asc_sign_index, retrograde=True)
    ketu_nav_idx = _navamsa_sign_index(ketu_lon)
    navamsa_planets["Ketu"] = PlanetPosition(
        name="Ketu",
        longitude=ketu_lon,
        sign_index=ketu_nav_idx,
        sign=RASHIS[ketu_nav_idx],
        sign_hindi=RASHI_HINDI[ketu_nav_idx],
        degree_in_sign=ketu_lon % SIGN_SPAN,
        nakshatra=planets["Ketu"].nakshatra,
        nakshatra_lord=planets["Ketu"].nakshatra_lord,
        pada=planets["Ketu"].pada,
        house=_house_from_ascendant(ketu_nav_idx, _navamsa_sign_index(asc_longitude)),
        retrograde=True,
    )

    return BirthChart(
        name=name,
        birth_datetime_local=dt_local,
        utc_offset_hours=utc_offset_hours,
        latitude=latitude,
        longitude=longitude,
        place_name=place_name,
        ascendant_longitude=asc_longitude,
        ascendant_sign_index=asc_sign_index,
        ascendant_sign=RASHIS[asc_sign_index],
        ascendant_sign_hindi=RASHI_HINDI[asc_sign_index],
        planets=planets,
        navamsa_planets=navamsa_planets,
    )


if __name__ == "__main__":
    # Quick manual smoke test - New Delhi, 15 Aug 1990, 2:30 PM IST
    chart = calculate_birth_chart(
        name="Test User",
        birth_date="1990-08-15",
        birth_time="14:30",
        utc_offset_hours=5.5,
        latitude=28.6139,
        longitude=77.2090,
        place_name="New Delhi, India",
    )
    import json
    print(json.dumps(chart.as_dict(), indent=2, ensure_ascii=False))