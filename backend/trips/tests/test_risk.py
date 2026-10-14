import pytest

from trips.domain.levels import RiskLevel
from trips.domain.risk import assess_weather, classify, load_adjusted_level
from trips.domain.thresholds import RAIN_BANDS, SNOW_BANDS, WIND_BANDS
from trips.domain.weather import Weather

LIGHT_LOAD = 10_000


@pytest.mark.parametrize(
    ("wind", "expected"),
    [
        (0, RiskLevel.LOW),
        (24.9, RiskLevel.LOW),
        (25, RiskLevel.MODERATE),
        (34, RiskLevel.MODERATE),
        (35, RiskLevel.HIGH),
        (44, RiskLevel.HIGH),
        (45, RiskLevel.SEVERE),
        (54, RiskLevel.SEVERE),
        (55, RiskLevel.NO_TRAVEL),
        (80, RiskLevel.NO_TRAVEL),
    ],
)
def test_wind_bands(wind, expected):
    assert classify(wind, WIND_BANDS) == expected


@pytest.mark.parametrize(
    ("rain", "expected"),
    [
        (0, RiskLevel.LOW),
        (0.09, RiskLevel.LOW),
        (0.10, RiskLevel.MODERATE),
        (0.24, RiskLevel.MODERATE),
        (0.25, RiskLevel.HIGH),
        (0.49, RiskLevel.HIGH),
        (0.50, RiskLevel.SEVERE),
        (1.00, RiskLevel.SEVERE),
        (1.01, RiskLevel.NO_TRAVEL),
    ],
)
def test_rain_bands(rain, expected):
    assert classify(rain, RAIN_BANDS) == expected


@pytest.mark.parametrize(
    ("snow", "expected"),
    [
        (0, RiskLevel.LOW),
        (0.49, RiskLevel.LOW),
        (0.5, RiskLevel.MODERATE),
        (0.99, RiskLevel.MODERATE),
        (1.0, RiskLevel.HIGH),
        (1.99, RiskLevel.HIGH),
        (2.0, RiskLevel.SEVERE),
        (3.0, RiskLevel.SEVERE),
        (3.01, RiskLevel.NO_TRAVEL),
    ],
)
def test_snow_bands(snow, expected):
    assert classify(snow, SNOW_BANDS) == expected


@pytest.mark.parametrize(
    ("wind", "load", "expected"),
    [
        (55, 1_000, RiskLevel.NO_TRAVEL),
        (60, 0, RiskLevel.NO_TRAVEL),
        (45, 30_001, RiskLevel.NO_TRAVEL),
        (54, 45_000, RiskLevel.NO_TRAVEL),
        (45, 30_000, RiskLevel.LOW),
        (44, 80_000, RiskLevel.SEVERE),
        (35, 40_001, RiskLevel.SEVERE),
        (35, 40_000, RiskLevel.LOW),
        (34, 80_000, RiskLevel.LOW),
    ],
)
def test_load_rules(wind, load, expected):
    assert load_adjusted_level(wind, load) == expected


def test_checkpoint_takes_worst_condition():
    weather = Weather(wind_mph=10, rain_in_per_hr=0.30, snow_in_per_hr=2.5)
    assert assess_weather(weather, LIGHT_LOAD) == RiskLevel.SEVERE


def test_heavy_load_escalates_high_wind_to_severe():
    weather = Weather(wind_mph=40, rain_in_per_hr=0, snow_in_per_hr=0)
    assert assess_weather(weather, LIGHT_LOAD) == RiskLevel.HIGH
    assert assess_weather(weather, 45_000) == RiskLevel.SEVERE


def test_load_rule_never_lowers_a_worse_condition():
    weather = Weather(wind_mph=40, rain_in_per_hr=1.5, snow_in_per_hr=0)
    assert assess_weather(weather, 45_000) == RiskLevel.NO_TRAVEL


def test_calm_weather_is_low():
    weather = Weather(wind_mph=5, rain_in_per_hr=0, snow_in_per_hr=0)
    assert assess_weather(weather, 80_000) == RiskLevel.LOW
