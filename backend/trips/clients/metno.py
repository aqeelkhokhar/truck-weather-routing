from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from django.conf import settings

from trips.clients.http import get_json
from trips.constants import (
    METNO_WORKERS,
    MM_PER_INCH,
    MS_TO_MPH,
    SECONDS_PER_HOUR,
    SNOW_TO_LIQUID_RATIO,
)
from trips.domain.weather import WeatherSeries

HOURLY_BLOCK = "next_1_hours"
SIX_HOUR_BLOCK = "next_6_hours"
BLOCK_HOURS = {HOURLY_BLOCK: 1, SIX_HOUR_BLOCK: 6}
SLEET_SNOW_SHARE = 0.5


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def precipitation_split(block, hours):
    liquid_in = block["details"].get("precipitation_amount", 0.0) / MM_PER_INCH / hours
    symbol = block["summary"]["symbol_code"]
    if "snow" in symbol:
        return 0.0, liquid_in * SNOW_TO_LIQUID_RATIO
    if "sleet" in symbol:
        return liquid_in * (
            1 - SLEET_SNOW_SHARE
        ), liquid_in * SLEET_SNOW_SHARE * SNOW_TO_LIQUID_RATIO
    return liquid_in, 0.0


def pick_block(data):
    for name in (HOURLY_BLOCK, SIX_HOUR_BLOCK):
        if name in data:
            return data[name], BLOCK_HOURS[name]
    return None, 1


def expand_timeseries(timeseries):
    winds, rains, snows = [], [], []
    for position, entry in enumerate(timeseries):
        moment = parse_time(entry["time"])
        following = (
            parse_time(timeseries[position + 1]["time"]) if position + 1 < len(timeseries) else None
        )
        span = round((following - moment).total_seconds() / SECONDS_PER_HOUR) if following else 1
        block, block_hours = pick_block(entry["data"])
        rain, snow = precipitation_split(block, block_hours) if block else (0.0, 0.0)
        wind = entry["data"]["instant"]["details"].get("wind_speed", 0.0) * MS_TO_MPH
        winds += [wind] * span
        rains += [rain] * span
        snows += [snow] * span
    return winds, rains, snows


def request_series(point):
    payload = get_json(
        settings.METNO_URL,
        params={"lat": point[0], "lon": point[1]},
        headers={"User-Agent": settings.WEATHER_USER_AGENT},
    )
    timeseries = payload["properties"]["timeseries"]
    winds, rains, snows = expand_timeseries(timeseries)
    return WeatherSeries(
        parse_time(timeseries[0]["time"]), tuple(winds), tuple(rains), tuple(snows)
    )


def fetch_series(points):
    with ThreadPoolExecutor(max_workers=METNO_WORKERS) as pool:
        return dict(zip(points, pool.map(request_series, points), strict=True))
