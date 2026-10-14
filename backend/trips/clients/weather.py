from django.core.cache import cache

from trips.clients import metno, openmeteo
from trips.clients.cache_keys import cache_key
from trips.constants import COORDINATE_PRECISION, WEATHER_CACHE_SECONDS
from trips.errors import ExternalServiceError

PROVIDERS = (openmeteo, metno)


def snap(point):
    return tuple(round(value, COORDINATE_PRECISION) for value in point)


def fetch_from_providers(points):
    for provider in PROVIDERS[:-1]:
        try:
            return provider.fetch_series(points)
        except ExternalServiceError:
            continue
    return PROVIDERS[-1].fetch_series(points)


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
