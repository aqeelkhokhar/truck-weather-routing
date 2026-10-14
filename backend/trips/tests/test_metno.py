import json
import re
from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs, urlparse

import pytest
import responses
from django.conf import settings

from trips.clients.metno import expand_timeseries, fetch_series, precipitation_split
from trips.clients.weather import fetch_forecasts
from trips.errors import ExternalServiceError

START = datetime(2026, 11, 1, 0, 0, tzinfo=UTC)


def stamp(hours):
    return (START + timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")


def hourly_entry(hours, wind, amount, symbol):
    return {
        "time": stamp(hours),
        "data": {
            "instant": {"details": {"wind_speed": wind}},
            "next_1_hours": {
                "summary": {"symbol_code": symbol},
                "details": {"precipitation_amount": amount},
            },
        },
    }


def six_hour_entry(hours, wind, amount, symbol):
    return {
        "time": stamp(hours),
        "data": {
            "instant": {"details": {"wind_speed": wind}},
            "next_6_hours": {
                "summary": {"symbol_code": symbol},
                "details": {"precipitation_amount": amount},
            },
        },
    }


def payload(*entries):
    return {"properties": {"timeseries": list(entries)}}


def test_rain_amount_is_converted_to_inches():
    block = {"summary": {"symbol_code": "rain"}, "details": {"precipitation_amount": 2.54}}
    assert precipitation_split(block, 1) == pytest.approx((0.1, 0.0))


def test_snow_uses_ten_to_one_ratio():
    block = {"summary": {"symbol_code": "heavysnow"}, "details": {"precipitation_amount": 2.54}}
    assert precipitation_split(block, 1) == pytest.approx((0.0, 1.0))


def test_sleet_is_split_between_rain_and_snow():
    block = {"summary": {"symbol_code": "sleet"}, "details": {"precipitation_amount": 2.54}}
    assert precipitation_split(block, 1) == pytest.approx((0.05, 0.5))


def test_six_hour_amounts_become_hourly_rates():
    block = {"summary": {"symbol_code": "rain"}, "details": {"precipitation_amount": 15.24}}
    assert precipitation_split(block, 6)[0] == pytest.approx(0.1)


def test_wind_is_converted_to_mph():
    winds, _, _ = expand_timeseries([hourly_entry(0, 10.0, 0.0, "cloudy")])
    assert winds[0] == pytest.approx(22.3694)


def test_timeseries_is_expanded_to_hourly_steps():
    entries = [
        hourly_entry(0, 5.0, 0.0, "cloudy"),
        hourly_entry(1, 6.0, 0.0, "cloudy"),
        six_hour_entry(2, 7.0, 0.0, "cloudy"),
        six_hour_entry(8, 8.0, 0.0, "cloudy"),
    ]
    winds, _, _ = expand_timeseries(entries)
    assert len(winds) == 2 + 6 + 1
    assert winds[1] == pytest.approx(6.0 * 2.23694)
    assert winds[7] == pytest.approx(7.0 * 2.23694)


def test_entry_without_precipitation_block_is_dry():
    entry = {"time": stamp(0), "data": {"instant": {"details": {"wind_speed": 1.0}}}}
    _, rains, snows = expand_timeseries([entry])
    assert (rains[0], snows[0]) == (0.0, 0.0)


@responses.activate
def test_fetch_series_builds_series_per_point():
    body = payload(hourly_entry(0, 5.0, 0.0, "cloudy"), hourly_entry(1, 6.0, 1.0, "rain"))
    responses.add(responses.GET, settings.METNO_URL, json=body)
    result = fetch_series([(10.0, 20.0)])
    assert result[(10.0, 20.0)].start == START
    assert result[(10.0, 20.0)].hours == 2


@responses.activate
def test_fetch_series_sends_identifying_user_agent():
    responses.add(responses.GET, settings.METNO_URL, json=payload(hourly_entry(0, 1.0, 0.0, "fog")))
    fetch_series([(10.0, 20.0)])
    assert responses.calls[0].request.headers["User-Agent"] == settings.WEATHER_USER_AGENT


@responses.activate
def test_falls_back_to_metno_when_open_meteo_is_rate_limited():
    responses.add(responses.GET, settings.WEATHER_URL, status=429)
    responses.add(responses.GET, settings.METNO_URL, json=payload(hourly_entry(0, 5.0, 0.0, "fog")))
    result = fetch_forecasts([(10.0, 20.0), (30.0, 40.0)])
    assert set(result) == {(10.0, 20.0), (30.0, 40.0)}


@responses.activate
def test_open_meteo_is_preferred_when_available():
    entry = {
        "hourly": {
            "time": [START.strftime("%Y-%m-%dT%H:%M")],
            "wind_speed_10m": [3.0],
            "rain": [0.0],
            "snowfall": [0.0],
        }
    }
    responses.add(responses.GET, settings.WEATHER_URL, json=entry)
    fetch_forecasts([(10.0, 20.0)])
    assert len(responses.calls) == 1
    assert "open-meteo" in responses.calls[0].request.url


@responses.activate
def test_fallback_requests_one_forecast_per_point():
    responses.add(responses.GET, settings.WEATHER_URL, status=429)

    def callback(request):
        query = parse_qs(urlparse(request.url).query)
        assert query["lat"] and query["lon"]
        return 200, {}, json.dumps(payload(hourly_entry(0, 2.0, 0.0, "fog")))

    responses.add_callback(
        responses.GET, re.compile(re.escape(settings.METNO_URL) + ".*"), callback
    )
    fetch_forecasts([(float(index), 20.0) for index in range(5)])
    assert len(responses.calls) == 1 + 5


@responses.activate
def test_error_surfaces_when_every_provider_fails():
    responses.add(responses.GET, settings.WEATHER_URL, status=429)
    responses.add(responses.GET, settings.METNO_URL, status=503)
    with pytest.raises(ExternalServiceError):
        fetch_forecasts([(10.0, 20.0)])
