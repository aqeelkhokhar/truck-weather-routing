import json
from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs, urlparse

import pytest
import responses
from django.conf import settings

from trips.clients.weather import fetch_forecasts, snap
from trips.domain.weather import WeatherSeries

START = datetime(2026, 11, 1, 0, 0, tzinfo=UTC)


def entry(winds, rains=None, snows=None):
    count = len(winds)
    times = [(START + timedelta(hours=hour)).strftime("%Y-%m-%dT%H:%M") for hour in range(count)]
    return {
        "hourly": {
            "time": times,
            "wind_speed_10m": winds,
            "rain": rains or [0.0] * count,
            "snowfall": snows or [0.0] * count,
        }
    }


def test_snap_rounds_to_forecast_grid():
    assert snap((41.87812, -87.62981)) == (41.88, -87.63)


def test_series_picks_nearest_hour():
    series = WeatherSeries(START, (1.0, 2.0, 3.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
    assert series.at(START + timedelta(minutes=70)).wind_mph == 2.0
    assert series.at(START + timedelta(minutes=100)).wind_mph == 3.0


def test_series_clamps_outside_range():
    series = WeatherSeries(START, (1.0, 2.0, 3.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
    assert series.at(START - timedelta(hours=5)).wind_mph == 1.0
    assert series.at(START + timedelta(hours=99)).wind_mph == 3.0


@responses.activate
def test_single_point_response_is_parsed():
    responses.add(responses.GET, settings.WEATHER_URL, json=entry([5.0, 6.0], [0.1, 0.2]))
    result = fetch_forecasts([(41.8781, -87.6298)])
    series = result[(41.88, -87.63)]
    assert series.winds_mph == (5.0, 6.0)
    assert series.rain_in_per_hr == (0.1, 0.2)
    assert series.start == START


@responses.activate
def test_batch_response_maps_each_point_in_order():
    body = [entry([1.0]), entry([2.0])]
    responses.add(responses.GET, settings.WEATHER_URL, json=body)
    result = fetch_forecasts([(10.0, 20.0), (30.0, 40.0)])
    assert result[(10.0, 20.0)].winds_mph == (1.0,)
    assert result[(30.0, 40.0)].winds_mph == (2.0,)


@responses.activate
def test_null_values_become_zero():
    responses.add(responses.GET, settings.WEATHER_URL, json=entry([None, 4.0]))
    series = fetch_forecasts([(10.0, 20.0)])[(10.0, 20.0)]
    assert series.winds_mph == (0.0, 4.0)


@responses.activate
def test_units_are_requested_in_mph_and_inches():
    responses.add(responses.GET, settings.WEATHER_URL, json=entry([1.0]))
    fetch_forecasts([(10.0, 20.0)])
    query = responses.calls[0].request.url
    assert "wind_speed_unit=mph" in query
    assert "precipitation_unit=inch" in query


@responses.activate
def test_duplicate_points_are_requested_once():
    responses.add(responses.GET, settings.WEATHER_URL, json=entry([1.0]))
    result = fetch_forecasts([(10.001, 20.001), (10.002, 20.002)])
    assert len(result) == 1
    assert "latitude=10.0&" in responses.calls[0].request.url


@responses.activate
def test_forecasts_are_cached():
    responses.add(responses.GET, settings.WEATHER_URL, json=entry([1.0]))
    fetch_forecasts([(10.0, 20.0)])
    fetch_forecasts([(10.0, 20.0)])
    assert len(responses.calls) == 1


@responses.activate
def test_large_requests_are_split_into_batches():
    points = [(float(index), 20.0) for index in range(120)]

    def callback(request):
        query = parse_qs(urlparse(request.url).query)
        count = len(query["latitude"][0].split(","))
        return 200, {}, json.dumps([entry([1.0])] * count)

    responses.add_callback(responses.GET, settings.WEATHER_URL, callback=callback)
    result = fetch_forecasts(points)
    assert len(result) == 120
    assert len(responses.calls) == 3


@pytest.mark.parametrize("hours", [1, 24])
def test_series_hours_property(hours):
    series = WeatherSeries(START, (0.0,) * hours, (0.0,) * hours, (0.0,) * hours)
    assert series.hours == hours
