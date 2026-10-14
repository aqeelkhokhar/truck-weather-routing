from datetime import UTC, datetime

from django.conf import settings
from django.core.cache import cache

from trips.clients.cache_keys import cache_key
from trips.clients.http import get_json
from trips.constants import (
    COORDINATE_PRECISION,
    FORECAST_FETCH_DAYS,
    WEATHER_BATCH_SIZE,
    WEATHER_CACHE_SECONDS,
)
from trips.domain.weather import WeatherSeries

HOURLY_FIELDS = ("wind_speed_10m", "rain", "snowfall")


def snap(point):
    return tuple(round(value, COORDINATE_PRECISION) for value in point)


def clean(values):
    return tuple(0.0 if value is None else float(value) for value in values)


def parse_series(entry):
    hourly = entry["hourly"]
    start = datetime.fromisoformat(hourly["time"][0]).replace(tzinfo=UTC)
    return WeatherSeries(
        start=start,
        winds_mph=clean(hourly["wind_speed_10m"]),
        rain_in_per_hr=clean(hourly["rain"]),
        snow_in_per_hr=clean(hourly["snowfall"]),
    )


def request_batch(points):
    payload = get_json(
        settings.WEATHER_URL,
        params={
            "latitude": ",".join(str(lat) for lat, _ in points),
            "longitude": ",".join(str(lon) for _, lon in points),
            "hourly": ",".join(HOURLY_FIELDS),
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
            "timezone": "UTC",
            "forecast_days": FORECAST_FETCH_DAYS,
        },
    )
    entries = payload if isinstance(payload, list) else [payload]
    return {point: parse_series(entry) for point, entry in zip(points, entries, strict=True)}


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
    for offset in range(0, len(missing), WEATHER_BATCH_SIZE):
        fetched = request_batch(missing[offset : offset + WEATHER_BATCH_SIZE])
        for point, forecast in fetched.items():
            cache.set(cache_key("weather", *point), forecast, WEATHER_CACHE_SECONDS)
            series[point] = forecast
    return series
