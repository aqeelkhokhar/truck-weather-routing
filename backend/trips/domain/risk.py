from trips.domain.levels import RiskLevel
from trips.domain.thresholds import LOAD_RULES, RAIN_BANDS, SNOW_BANDS, WIND_BANDS


def classify(value, bands):
    for band in bands:
        if band.reached_by(value):
            return band.level
    return RiskLevel.LOW


def load_adjusted_level(wind_mph, load_lb):
    levels = [rule.level for rule in LOAD_RULES if rule.applies_to(wind_mph, load_lb)]
    return max(levels, default=RiskLevel.LOW)


def assess_weather(weather, load_lb):
    return max(
        classify(weather.wind_mph, WIND_BANDS),
        classify(weather.rain_in_per_hr, RAIN_BANDS),
        classify(weather.snow_in_per_hr, SNOW_BANDS),
        load_adjusted_level(weather.wind_mph, load_lb),
    )
