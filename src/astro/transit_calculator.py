"""
transit_calculator.py

Real transiting (current/future) planetary positions, mapped onto a person's
NATAL chart houses, for month-by-month predictions.

WHY this is a separate module from chart_calculator.py: a "transit" is a
totally different kind of fact than a natal placement. A natal placement is
fixed forever once someone is born. A transit is "where is Saturn RIGHT NOW
(or on some future date), and which of THIS PERSON's houses does that fall
into." Same ephemeris math under the hood, different question being asked -
kept separate so neither file gets muddled about which one it's answering.

Classical technique used here: transiting planet positions are computed for
a target date, then each transiting planet's sign is converted to a house
number using the person's NATAL ascendant sign as the reference point (NOT
a "chart for that day" with its own ascendant - the natal ascendant stays
fixed as the frame of reference, which is the standard Vedic Gochar method).

We deliberately exclude the Moon from "monthly relevant" flags even though
we still compute its position - the Moon changes sign every ~2.25 days, so
at monthly resolution it has no stable meaning. Real astrologers use Moon
transits for daily/weekly predictions, not monthly ones. Sun/Mars/Mercury/
Venus/Jupiter/Saturn/Rahu/Ketu are the planets whose sign occupancy actually
holds steady for a meaningful chunk of a given month.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import swisseph as swe

from astro.chart_calculator import (
    PLANET_IDS,
    RASHIS,
    RASHI_HINDI,
    PlanetPosition,
    BirthChart,
    _house_from_ascendant,
    _build_planet_position,
)

# Planets whose sign occupancy is stable enough to matter for a MONTHLY
# (not daily) prediction. Moon deliberately excluded - see module docstring.
MONTHLY_RELEVANT_PLANETS = [
    "Sun", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu",
]


@dataclass
class MonthlyTransit:
    month_label: str            # e.g. "September 2026"
    period_start: date
    period_end: date
    snapshot_date: date         # the actual date the positions were calculated for (mid-month)
    planets: dict = field(default_factory=dict)     # name -> PlanetPosition, house = relative to NATAL ascendant
    ingresses: list = field(default_factory=list)    # planets that changed sign since last month - the real "news" of a month
    stations: list = field(default_factory=list)      # planets that turned retrograde/direct since last month - classically very strong trigger points
    sade_sati_phase: str | None = None                 # None, "Rising Phase", "Peak Phase", or "Setting Phase" - only set when Saturn is transiting natal Moon sign +/- 1

    def as_dict(self) -> dict:
        return {
            "month_label": self.month_label,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "planets": {name: p.as_dict() for name, p in self.planets.items()},
            "ingresses": self.ingresses,
            "stations": self.stations,
            "sade_sati_phase": self.sade_sati_phase,
        }


def _add_months(d: date, n: int) -> date:
    """
    Plain calendar month arithmetic without pulling in python-dateutil as a
    new dependency - we only ever need "add N whole months," which this
    handles fine including year rollover and Dec->Jan wraparound.
    """
    month_index = d.month - 1 + n
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)


def _month_end(d: date) -> date:
    """Last day of the month containing d, without a calendar library."""
    next_month_start = _add_months(date(d.year, d.month, 1), 1)
    return next_month_start.replace(day=1)  # caller treats period_end as exclusive-ish label bound; see usage below


def calculate_transit_positions(
    target_date: date,
    natal_ascendant_sign_index: int,
    ayanamsa: int = swe.SIDM_LAHIRI,
) -> dict[str, PlanetPosition]:
    """
    Real planetary positions for target_date, with each planet's .house
    field computed relative to the NATAL ascendant (not a fresh ascendant
    for target_date - Gochar is about where transiting planets fall in
    the person's own fixed chart, not a new chart for "today").

    Uses noon UTC as the snapshot time. For monthly-resolution predictions
    the exact hour doesn't matter - none of the slow planets we care about
    (see MONTHLY_RELEVANT_PLANETS) move enough within a single day to
    change sign, so noon is just a stable, arbitrary anchor.
    """
    swe.set_sid_mode(ayanamsa)

    jd_ut = swe.julday(target_date.year, target_date.month, target_date.day, 12.0)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    positions: dict[str, PlanetPosition] = {}
    raw_longitudes: dict[str, float] = {}

    for pname, pid in PLANET_IDS.items():
        calc_result = swe.calc_ut(jd_ut, pid, flags)
        result = calc_result[0]  # same 3-vs-2-value quirk handled the same way as chart_calculator.py
        lon = result[0] % 360.0
        speed = result[3]
        raw_longitudes[pname] = lon
        positions[pname] = _build_planet_position(
            pname, lon, natal_ascendant_sign_index, retrograde=speed < 0
        )

    # Ketu = Rahu + 180, same convention as chart_calculator.py
    ketu_lon = (raw_longitudes["Rahu"] + 180.0) % 360.0
    positions["Ketu"] = _build_planet_position(
        "Ketu", ketu_lon, natal_ascendant_sign_index, retrograde=True
    )

    return positions


def _detect_sade_sati(saturn_sign_index: int, natal_moon_sign_index: int) -> str | None:
    """
    Sade Sati: the classically significant ~7.5-year period when transiting
    Saturn moves through the sign before, the sign of, and the sign after
    the person's natal Moon sign. Worth flagging explicitly since it's one
    of the most commonly asked-about transits in real consultations.
    """
    offset = (saturn_sign_index - natal_moon_sign_index) % 12
    if offset == 11:   # one sign BEHIND natal Moon sign
        return "Rising Phase (first Dhaiya)"
    if offset == 0:    # SAME sign as natal Moon
        return "Peak Phase"
    if offset == 1:    # one sign AHEAD of natal Moon sign
        return "Setting Phase (last Dhaiya)"
    return None


def calculate_monthly_transits(
    natal_chart: BirthChart,
    start_date: date | None = None,
    months: int = 12,
) -> list[MonthlyTransit]:
    """
    One MonthlyTransit per month, starting from the current month, for
    `months` months forward. Snapshot is taken on the 15th of each month
    (a stable mid-month anchor - avoids first/last-day-of-month edge
    ambiguity for which "month" a planet near a sign boundary belongs to).

    ingresses/stations are computed by diffing each month's snapshot
    against the previous one - these are the actual narrative hooks (e.g.
    "Jupiter moves into your 5th house this month") rather than just
    restating the same static position 12 times.
    """
    if start_date is None:
        start_date = date.today()

    results: list[MonthlyTransit] = []
    previous_positions: dict[str, PlanetPosition] | None = None

    for i in range(months):
        month_start = _add_months(date(start_date.year, start_date.month, 1), i)
        month_end = _add_months(month_start, 1)  # exclusive upper bound (first day of next month)
        snapshot_date = month_start.replace(day=15)

        positions = calculate_transit_positions(
            snapshot_date, natal_chart.ascendant_sign_index
        )

        ingresses: list[str] = []
        stations: list[str] = []
        if previous_positions is not None:
            for pname in MONTHLY_RELEVANT_PLANETS:
                prev = previous_positions[pname]
                curr = positions[pname]
                if prev.sign != curr.sign:
                    ingresses.append(
                        f"{pname} moves from {prev.sign} into {curr.sign} "
                        f"(natal house {curr.house})"
                    )
                if prev.retrograde != curr.retrograde:
                    direction = "turns retrograde" if curr.retrograde else "turns direct"
                    stations.append(f"{pname} {direction} in {curr.sign} (natal house {curr.house})")

        sade_sati = _detect_sade_sati(
            positions["Saturn"].sign_index,
            natal_chart.planets["Moon"].sign_index,
        )

        results.append(
            MonthlyTransit(
                month_label=month_start.strftime("%B %Y"),
                period_start=month_start,
                period_end=month_end,
                snapshot_date=snapshot_date,
                planets=positions,
                ingresses=ingresses,
                stations=stations,
                sade_sati_phase=sade_sati,
            )
        )

        previous_positions = positions

    return results


if __name__ == "__main__":
    # Smoke test: reuse the same test person as chart_calculator.py's own
    # smoke test so results are easy to sanity-check against each other.
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

    monthly = calculate_monthly_transits(chart, months=12)
    for m in monthly:
        print(f"\n=== {m.month_label} ===")
        print(f"Sade Sati: {m.sade_sati_phase}")
        if m.ingresses:
            print("Ingresses:", m.ingresses)
        if m.stations:
            print("Stations:", m.stations)
        for pname in MONTHLY_RELEVANT_PLANETS:
            p = m.planets[pname]
            retro = " (R)" if p.retrograde else ""
            print(f"  {pname}: {p.sign} house {p.house}{retro}")