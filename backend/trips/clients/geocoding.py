from dataclasses import dataclass

from django.conf import settings
from django.core.cache import cache

from trips.clients.cache_keys import cache_key
from trips.clients.http import get_json
from trips.constants import GEOCODE_CACHE_SECONDS
from trips.errors import LocationNotFoundError


@dataclass(frozen=True)
class Location:
    name: str
    lat: float
    lon: float


def geocode(query):
    key = cache_key("geocode", query.strip().lower())
    cached = cache.get(key)
    if cached:
        return cached
    results = get_json(
        settings.GEOCODER_URL,
        params={"q": query, "format": "jsonv2", "limit": 1},
        headers={"User-Agent": settings.GEOCODER_USER_AGENT},
    )
    if not results:
        raise LocationNotFoundError
    best = results[0]
    location = Location(best["display_name"], float(best["lat"]), float(best["lon"]))
    cache.set(key, location, GEOCODE_CACHE_SECONDS)
    return location
