"""
geocoding.py

Converts a "Place of Birth" text input into what chart_calculator.py actually
needs: latitude, longitude, and a precise UTC offset for the exact birth date.

Fully offline - no network calls at runtime:
    - City name -> (lat, lon):   geopointdb  (bundled SQLite of 200k+ world cities)
    - (lat, lon) -> IANA tz name: timezonefinder (bundled timezone boundary data)
    - IANA tz name + date -> UTC offset in hours: Python's built-in zoneinfo

Why not just hardcode UTC+5:30 for everything?
Because although all of India uses a single offset today (Asia/Kolkata,
no DST), the platform's requirements don't rule out non-Indian birthplaces
(e.g. NRI users), and some countries have DST or have changed their offset
historically. Computing the REAL offset for the REAL date is what keeps this
in line with the "no hallucinated/approximated astronomy" principle the
whole calculation layer is built on.

Install:
    pip install geopointdb timezonefinder
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from zoneinfo import ZoneInfo

from geopointdb.getpoint import LatLonFinder
from timezonefinder import TimezoneFinder

# Both of these load bundled local data files on first use - no network call.
_tz_finder = TimezoneFinder()


@dataclass
class ResolvedLocation:
    query: str                 # what the user typed
    matched_city: str          # the city name actually matched in the database
    country: str
    latitude: float
    longitude: float
    timezone_name: str         # IANA name, e.g. "Asia/Kolkata"
    utc_offset_hours: float    # precise offset for the given birth date

    def as_dict(self) -> dict:
        return {
            "query": self.query,
            "matched_city": self.matched_city,
            "country": self.country,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone_name": self.timezone_name,
            "utc_offset_hours": self.utc_offset_hours,
        }


class PlaceNotFoundError(Exception):
    """Raised when the place name has no match in the offline database."""


class AmbiguousPlaceError(Exception):
    """Raised when multiple equally-plausible cities share the name and we
    need the caller (frontend) to ask the user to disambiguate."""

    def __init__(self, query: str, candidates: list[dict]):
        self.query = query
        self.candidates = candidates
        names = ", ".join(f"{c['city']}, {c['country']}" for c in candidates[:5])
        super().__init__(f"Multiple matches for '{query}': {names}. Please specify country.")

    def candidate_labels(self) -> list[str]:
        """
        Human-readable labels for each candidate, for showing in a picker
        (e.g. a Streamlit selectbox) - "Gorakhpur, India (Uttar Pradesh)"
        when we can guess the state, otherwise just city/country/coordinates
        so at least SOMETHING distinguishes the options.
        """
        labels = []
        for c in self.candidates:
            state_guess = _guess_state_label(c["lat"], c["lon"])
            if state_guess:
                labels.append(f"{c['city']}, {c['country']} ({state_guess})")
            else:
                labels.append(f"{c['city']}, {c['country']} (lat {c['lat']:.2f}, lon {c['lon']:.2f})")
        return labels


# Approximate bounding boxes for Indian states/UTs (lat_min, lat_max, lon_min,
# lon_max). Used ONLY to disambiguate when multiple cities share an identical
# name (e.g. there's a "Gorakhpur" in both Haryana and Uttar Pradesh, and the
# offline city database gives us no state field to tell them apart directly).
# Not exhaustive - covers the states most likely to actually come up. If a
# state name isn't in here, disambiguation just falls back to asking the user.
INDIAN_STATE_BOUNDING_BOXES = {
    "uttar pradesh": (23.8, 30.4, 77.0, 84.7),
    "haryana": (27.6, 30.9, 74.5, 77.6),
    "bihar": (24.2, 27.5, 83.3, 88.1),
    "rajasthan": (23.0, 30.2, 69.5, 78.3),
    "madhya pradesh": (21.1, 26.9, 74.0, 82.8),
    "maharashtra": (15.6, 22.0, 72.6, 80.9),
    "gujarat": (20.1, 24.7, 68.1, 74.5),
    "punjab": (29.5, 32.5, 73.9, 76.9),
    "west bengal": (21.5, 27.2, 85.8, 89.9),
    "karnataka": (11.6, 18.5, 74.0, 78.6),
    "tamil nadu": (8.1, 13.6, 76.2, 80.4),
    "andhra pradesh": (12.6, 19.9, 76.8, 84.8),
    "telangana": (15.8, 19.9, 77.2, 81.3),
    "kerala": (8.2, 12.8, 74.9, 77.4),
    "odisha": (17.8, 22.6, 81.4, 87.5),
    "uttarakhand": (28.7, 31.5, 77.6, 81.1),
    "delhi": (28.4, 28.9, 76.8, 77.3),
    "jharkhand": (21.9, 25.4, 83.3, 87.6),
    "chhattisgarh": (17.8, 24.1, 80.2, 84.4),
    "assam": (24.1, 28.2, 89.7, 96.0),
}


def _place_and_state(place_name: str) -> tuple[str, str | None]:
    """
    Splits "Gorakhpur, Uttar Pradesh" into ("Gorakhpur", "uttar pradesh").
    The offline city database only matches on plain city names, so the state
    part (if any) is pulled out here and used later only for disambiguation,
    never sent into the actual city lookup itself.
    """
    if "," in place_name:
        city_part, state_part = place_name.split(",", 1)
        return city_part.strip(), state_part.strip().lower()
    return place_name.strip(), None


def _guess_state_label(lat: float, lon: float) -> str | None:
    """
    Best-effort reverse lookup: given coordinates, which of our known state
    bounding boxes (if any) do they fall inside? Purely for showing the user
    a readable label like "Gorakhpur (Uttar Pradesh)" when picking between
    ambiguous candidates - not authoritative, just a helpful guess.
    """
    for state_name, (lat_min, lat_max, lon_min, lon_max) in INDIAN_STATE_BOUNDING_BOXES.items():
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return state_name.title()
    return None


def _utc_offset_for_date(timezone_name: str, on_date: date) -> float:
    """
    Returns the UTC offset in hours for a given IANA timezone name on a
    specific calendar date (matters for places with historical DST changes;
    doesn't matter for India, which has had a fixed +5:30 offset since 1947).
    """
    tz = ZoneInfo(timezone_name)
    # Use noon on that date to avoid any edge-case ambiguity right at a
    # DST transition boundary.
    dt = datetime(on_date.year, on_date.month, on_date.day, 12, 0, tzinfo=tz)
    offset = dt.utcoffset()
    return offset.total_seconds() / 3600.0


def resolve_from_candidate(candidate: dict, place_name: str, birth_date: date) -> ResolvedLocation:
    """
    Skips the whole search/disambiguation process and builds a
    ResolvedLocation directly from a candidate dict the user already picked
    (e.g. from an AmbiguousPlaceError's .candidates, after showing them in a
    Streamlit selectbox). Use this for the "let the user choose" flow instead
    of trying to make resolve_place() guess on its own.
    """
    lat, lon = candidate["lat"], candidate["lon"]
    tz_name = _tz_finder.timezone_at(lat=lat, lng=lon)
    if tz_name is None:
        raise PlaceNotFoundError(
            f"Could not resolve a timezone for lat={lat}, lon={lon}. "
            f"This shouldn't normally happen on land."
        )
    utc_offset = _utc_offset_for_date(tz_name, birth_date)
    return ResolvedLocation(
        query=place_name,
        matched_city=candidate["city"],
        country=candidate["country"],
        latitude=lat,
        longitude=lon,
        timezone_name=tz_name,
        utc_offset_hours=utc_offset,
    )


def resolve_place(
    place_name: str,
    birth_date: date,
    country_hint: str | None = None,
) -> ResolvedLocation:
    """
    place_name: free text as typed by the user, e.g. "Kanpur" or
                "Gorakhpur, Uttar Pradesh" (a trailing state name is allowed
                and used only for disambiguation, see _place_and_state above -
                the offline database itself only knows plain city names, so
                sending "City, State" straight into it just returns nothing).
    birth_date: the person's actual birth date (a `datetime.date`), used to
                compute the correct historical UTC offset
    country_hint: optional, e.g. "India" - disambiguates when multiple
                  cities worldwide share the same name

    Raises PlaceNotFoundError if nothing matches, or AmbiguousPlaceError if
    multiple candidates remain even after country/state narrowing.
    """
    city_only, state_hint = _place_and_state(place_name)

    finder = LatLonFinder()
    try:
        matches = finder.find_city(city_only)
    finally:
        finder.close()

    if not matches:
        raise PlaceNotFoundError(
            f"No city found matching '{city_only}'. Check spelling, or try "
            f"a nearby larger city/district headquarters instead."
        )

    if country_hint:
        filtered = [m for m in matches if m["country"].lower() == country_hint.lower()]
        if filtered:
            matches = filtered

    if len(matches) > 1:
        # Prefer an exact case-insensitive name match over partial matches
        exact = [m for m in matches if m["city"].lower() == city_only.lower()]
        if len(exact) >= 1:
            matches = exact

    if len(matches) > 1 and state_hint and state_hint in INDIAN_STATE_BOUNDING_BOXES:
        # this is the actual fix for the Gorakhpur situation - two cities can
        # share an exact name, so the only way to tell them apart (since the
        # database has no state field at all) is to check which one's
        # coordinates actually fall inside the state the user typed.
        lat_min, lat_max, lon_min, lon_max = INDIAN_STATE_BOUNDING_BOXES[state_hint]
        narrowed = [
            m for m in matches
            if lat_min <= m["lat"] <= lat_max and lon_min <= m["lon"] <= lon_max
        ]
        if len(narrowed) == 1:
            matches = narrowed

    if len(matches) > 1:
        raise AmbiguousPlaceError(place_name, matches)

    match = matches[0]
    lat, lon = match["lat"], match["lon"]

    tz_name = _tz_finder.timezone_at(lat=lat, lng=lon)
    if tz_name is None:
        raise PlaceNotFoundError(
            f"Found coordinates for '{city_only}' but could not resolve a timezone "
            f"for lat={lat}, lon={lon}. This shouldn't normally happen on land."
        )

    utc_offset = _utc_offset_for_date(tz_name, birth_date)

    return ResolvedLocation(
        query=place_name,
        matched_city=match["city"],
        country=match["country"],
        latitude=lat,
        longitude=lon,
        timezone_name=tz_name,
        utc_offset_hours=utc_offset,
    )


if __name__ == "__main__":
    import json

    for place in ["Kanpur", "New Delhi", "Mumbai", "London", "New York"]:
        try:
            result = resolve_place(place, birth_date=date(1990, 8, 15))
            print(json.dumps(result.as_dict(), indent=2, ensure_ascii=False))
        except (PlaceNotFoundError, AmbiguousPlaceError) as e:
            print(f"{place}: {e}")