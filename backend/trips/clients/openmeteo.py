from datetime import UTC, datetime

from django.conf import settings

from trips.clients.http import get_json
from trips.constants import FORECAST_FETCH_DAYS, WEATHER_BATCH_SIZE
from trips.domain.weather import WeatherSeries

HOURLY_FIELDS = ("wind_speed_10m", "rain", "snowfall")


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


def fetch_series(points):
    series = {}
    for offset in range(0, len(points), WEATHER_BATCH_SIZE):
        series.update(request_batch(points[offset : offset + WEATHER_BATCH_SIZE]))
    return series
