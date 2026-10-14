from django.core.cache import cache

from trips.clients import metno, openmeteo
from trips.clients.cache_keys import cache_key
from trips.constants import COORDINATE_PRECISION, PROVIDER_COOLDOWN_SECONDS, WEATHER_CACHE_SECONDS
from trips.errors import ExternalServiceError

COOLDOWN_KEY = cache_key("weather-provider-cooldown", "openmeteo")


def snap(point):
    return tuple(round(value, COORDINATE_PRECISION) for value in point)


def fetch_from_providers(points):
    if not cache.get(COOLDOWN_KEY):
        try:
            return openmeteo.fetch_series(points)
        except ExternalServiceError:
            cache.set(COOLDOWN_KEY, True, PROVIDER_COOLDOWN_SECONDS)
    return metno.fetch_series(points)


def fetch_forecasts(points):
    snapped = list(dict.fromkeys(snap(point) for point in points))
    series = {}
    missing = []
    for point in snapped:
        cached = cache.get(cache_key("weather", *point))
        if cached:
            series[point] = cached
        else:
            missing.append(point)
    if missing:
        for point, forecast in fetch_from_providers(missing).items():
            cache.set(cache_key("weather", *point), forecast, WEATHER_CACHE_SECONDS)
            series[point] = forecast
    return series
